"""Private Gmail adapter. Tokens remain in the bridge's owner-only state directory."""
import base64
import concurrent.futures
import hashlib
import html
import json
import os
import re
import secrets
import sqlite3
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from email.message import EmailMessage
from email.policy import SMTP
from email.utils import getaddresses, parseaddr
from html.parser import HTMLParser
from pathlib import Path

CONFIG = Path.home() / '.config/inxs-dashboard/gmail-oauth.json'
STATE = Path.home() / '.local/state/inxs-dashboard/mail'
CALLBACK = 'https://inxs.live/email/oauth/callback'
SCOPE = 'https://www.googleapis.com/auth/gmail.modify'
DEFAULT_EMAIL = 'lexiinxs@gmail.com'
LOCK = threading.RLock()
ID = re.compile(r'^[A-Za-z0-9_-]{1,256}$')


class MailError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def database():
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(STATE, 0o700)
    dbfile = STATE / 'mail.sqlite3'
    if not dbfile.exists():
        dbfile.touch(mode=0o600, exist_ok=True)
    os.chmod(dbfile, 0o600)
    db = sqlite3.connect(dbfile, timeout=10)
    db.row_factory = sqlite3.Row
    db.executescript('''
        CREATE TABLE IF NOT EXISTS accounts (
            email TEXT PRIMARY KEY, refresh TEXT NOT NULL, access TEXT NOT NULL,
            expires REAL NOT NULL, connected REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS pending (
            state TEXT PRIMARY KEY, session TEXT NOT NULL, verifier TEXT NOT NULL,
            email TEXT NOT NULL, expires REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS sent_requests (
            request TEXT PRIMARY KEY, email TEXT NOT NULL, result TEXT, created REAL NOT NULL);
    ''')
    return db


def config():
    try:
        raw = json.loads(CONFIG.read_text())
        data = raw.get('web', raw)
        if not data.get('client_id') or not data.get('client_secret'):
            return None
        return data
    except (OSError, ValueError, TypeError, AttributeError):
        return None


def request_json(url, *, data=None, token=None, method=None):
    headers = {'Accept': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    if data is not None:
        if url == 'https://oauth2.googleapis.com/token':
            body = urllib.parse.urlencode(data).encode()
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        else:
            body = json.dumps(data).encode()
            headers['Content-Type'] = 'application/json'
    else:
        body = None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            return json.loads(response.read(16 * 1024 * 1024))
    except urllib.error.HTTPError as exc:
        # Never return provider error bodies, auth codes, tokens, or message content.
        if exc.code in (400, 401) and ('oauth2' in url or exc.code == 401):
            raise MailError('Google authorization expired or was rejected. Reconnect this account.', 409) from None
        if exc.code == 403:
            raise MailError('Google denied access. Check Gmail API access and reconnect with the requested permissions.', 403) from None
        if exc.code == 404:
            raise MailError('This message is no longer available.', 404) from None
        if exc.code == 429:
            raise MailError('Google is limiting requests. Please wait and try again.', 429) from None
        raise MailError('Google could not complete this request. Please try again.', 502) from None
    except (OSError, ValueError):
        raise MailError('The Gmail connection is temporarily unavailable.', 502) from None


def b64(data):
    return base64.urlsafe_b64encode(data).decode().rstrip('=')


def unb64(value):
    return base64.urlsafe_b64decode(value + '=' * (-len(value) % 4))


def email_address(value):
    value = str(value).strip().lower()
    if not re.fullmatch(r'[a-z0-9.!#$%&\x27*+/=?^_`{|}~-]+@gmail\.com', value):
        raise MailError('Enter a personal @gmail.com address.')
    return value


def item_id(value):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise MailError('Invalid message or attachment.')
    return value


def access_token(email):
    # Serialize refreshes so concurrent inbox reads do not overwrite token updates.
    with LOCK, database() as db:
        row = db.execute('SELECT * FROM accounts WHERE email=?', (email,)).fetchone()
        if row is None:
            raise MailError('Connect this Gmail account first.', 409)
        if row['expires'] > time.time() + 90:
            return row['access']
        client = config()
        if not client:
            raise MailError('Google connection setup is not complete.', 503)
        result = request_json('https://oauth2.googleapis.com/token', data={
            'client_id': client['client_id'], 'client_secret': client['client_secret'],
            'refresh_token': row['refresh'], 'grant_type': 'refresh_token'})
        db.execute('UPDATE accounts SET access=?,expires=?,refresh=? WHERE email=?', (
            result['access_token'], time.time() + result.get('expires_in', 3600),
            result.get('refresh_token', row['refresh']), email))
        return result['access_token']


def gmail(email, path, data=None, token=None, method=None):
    return request_json('https://gmail.googleapis.com/gmail/v1/users/me/' + path,
                        data=data, token=token or access_token(email), method=method)


def status():
    with database() as db:
        accounts = [{'email': row['email'], 'connectedAt': row['connected']}
                    for row in db.execute('SELECT email,connected FROM accounts ORDER BY connected')]
    return {'configured': bool(config()), 'accounts': accounts, 'firstEmail': DEFAULT_EMAIL}


def unread():
    state = status()
    if not state['accounts']:
        return {'connected': False, 'configured': state['configured'], 'unread': None}
    def count(account):
        try:
            data = gmail(account['email'], 'labels/INBOX')
            return {'email': account['email'], 'unread': int(data.get('messagesUnread', 0))}
        except MailError:
            return {'email': account['email'], 'unread': None}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        counts = list(pool.map(count, state['accounts']))
    complete = all(item['unread'] is not None for item in counts)
    return {'connected': True, 'unread': sum(item['unread'] or 0 for item in counts) if complete else None,
            'checkedAt': time.time(), 'accounts': counts}


def connect(data, session):
    client = config()
    if not client:
        raise MailError('Google connection setup is needed before you can sign in.', 503)
    email = email_address(data.get('email', DEFAULT_EMAIL))
    state, verifier = secrets.token_urlsafe(32), secrets.token_urlsafe(64)
    with database() as db:
        db.execute('DELETE FROM pending WHERE expires < ?', (time.time(),))
        db.execute('INSERT INTO pending VALUES (?,?,?,?,?)', (
            hashlib.sha256(state.encode()).hexdigest(), session, verifier, email, time.time() + 600))
    query = urllib.parse.urlencode({
        'client_id': client['client_id'], 'redirect_uri': CALLBACK,
        'response_type': 'code', 'scope': SCOPE, 'access_type': 'offline',
        'prompt': 'consent', 'login_hint': email, 'state': state,
        'code_challenge': b64(hashlib.sha256(verifier.encode()).digest()),
        'code_challenge_method': 'S256'})
    return {'url': 'https://accounts.google.com/o/oauth2/v2/auth?' + query}


def callback(data, session):
    state = data.get('state', '')
    if not isinstance(state, str) or not 20 <= len(state) <= 200:
        raise MailError('This connection link is invalid. Start again.')
    digest = hashlib.sha256(state.encode()).hexdigest()
    with LOCK, database() as db:
        row = db.execute('SELECT * FROM pending WHERE state=? AND session=? AND expires>?',
                         (digest, session, time.time())).fetchone()
        if row is None:
            raise MailError('This connection link has expired or belongs to another session. Start again.')
        db.execute('DELETE FROM pending WHERE state=?', (digest,))
    if data.get('error'):
        raise MailError('Google sign-in was cancelled. You can connect again whenever you are ready.')
    code = data.get('code', '')
    if not isinstance(code, str) or not code or len(code) > 4096:
        raise MailError('Google did not return a valid authorization code.')
    client = config()
    if not client:
        raise MailError('Google connection setup is not complete.', 503)
    result = request_json('https://oauth2.googleapis.com/token', data={
        'client_id': client['client_id'], 'client_secret': client['client_secret'],
        'code': code, 'code_verifier': row['verifier'], 'redirect_uri': CALLBACK,
        'grant_type': 'authorization_code'})
    if SCOPE not in result.get('scope', '').split():
        raise MailError('Gmail permission was not granted. Reconnect and approve email access.', 403)
    profile = gmail(row['email'], 'profile', token=result['access_token'])
    actual = profile['emailAddress'].lower()
    if actual != row['email']:
        raise MailError('The selected Google account does not match the requested Gmail address.', 403)
    with database() as db:
        old = db.execute('SELECT refresh FROM accounts WHERE email=?', (actual,)).fetchone()
        refresh = result.get('refresh_token') or (old['refresh'] if old else '')
        if not refresh:
            raise MailError('Google did not grant ongoing access. Reconnect and approve access.', 409)
        db.execute('INSERT OR REPLACE INTO accounts VALUES (?,?,?,?,?)', (
            actual, refresh, result['access_token'], time.time() + result.get('expires_in', 3600), time.time()))
    return {'connected': actual}


def header(message, name):
    return next((h.get('value', '') for h in message.get('payload', {}).get('headers', [])
                 if h.get('name', '').lower() == name.lower()), '')


def summary(message):
    return {'id': message['id'], 'threadId': message.get('threadId', ''),
            'subject': header(message, 'subject') or '(No subject)',
            'from': header(message, 'from'), 'to': header(message, 'to'),
            'replyTo': header(message, 'reply-to') or header(message, 'from'),
            'date': header(message, 'date'), 'messageId': header(message, 'message-id'),
            'snippet': html.unescape(message.get('snippet', '')),
            'unread': 'UNREAD' in message.get('labelIds', []),
            'starred': 'STARRED' in message.get('labelIds', [])}


class PlainHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self.blocked = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'head'):
            self.blocked += 1
        if not self.blocked and tag in ('p', 'div', 'br', 'li', 'tr', 'h1', 'h2', 'h3'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'head') and self.blocked:
            self.blocked -= 1

    def handle_data(self, data):
        if not self.blocked:
            self.parts.append(data)


def body_parts(payload):
    plain, markup, attachments = [], [], []

    def visit(part):
        body = part.get('body', {})
        filename = part.get('filename')
        if filename and body.get('attachmentId'):
            attachments.append({'id': body['attachmentId'], 'name': filename, 'size': body.get('size', 0)})
            return
        content = body.get('data')
        if content and part.get('mimeType') in ('text/plain', 'text/html') and not filename:
            decoded = unb64(content).decode('utf-8', errors='replace')
            (plain if part['mimeType'] == 'text/plain' else markup).append(decoded)
        for child in part.get('parts', []):
            visit(child)
    visit(payload)
    if plain:
        text = '\n\n'.join(plain)
    else:
        parser = PlainHTML()
        parser.feed('\n'.join(markup))
        text = ''.join(parser.parts)
    return text[:1000000], attachments


def messages(query):
    email = email_address(query.get('account', ''))
    folder = query.get('folder', 'INBOX')
    if folder not in ('INBOX', 'STARRED', 'SENT', 'DRAFT', 'TRASH'):
        raise MailError('Unknown email folder.')
    search = query.get('q', '')
    page = query.get('page', '')
    if len(search) > 500 or len(page) > 2048:
        raise MailError('Search is too long.')
    params = {'maxResults': 20, 'labelIds': folder}
    if folder == 'TRASH':
        params['includeSpamTrash'] = 'true'
    if search:
        params['q'] = search
    if page:
        params['pageToken'] = page
    token = access_token(email)
    result = gmail(email, 'messages?' + urllib.parse.urlencode(params), token=token)
    ids = [item_id(m['id']) for m in result.get('messages', [])]
    def load(mid):
        return summary(gmail(email, 'messages/' + mid + '?format=metadata', token=token))
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        items = list(pool.map(load, ids))
    return {'messages': items, 'nextPage': result.get('nextPageToken', ''), 'account': email}


def message(query):
    email, mid = email_address(query.get('account', '')), item_id(query.get('id'))
    raw = gmail(email, 'messages/' + mid + '?format=full')
    text, attachments = body_parts(raw.get('payload', {}))
    return {**summary(raw), 'body': text or '(This message has no displayable text.)', 'attachments': attachments}


def modify(data):
    email, mid = email_address(data.get('account', '')), item_id(data.get('id'))
    if data.get('action') == 'restore':
        gmail(email, 'messages/' + mid + '/untrash', method='POST')
        try:
            gmail(email, 'messages/' + mid + '/modify',
                  {'addLabelIds': ['INBOX'], 'removeLabelIds': ['SPAM']})
        except MailError as exc:
            raise MailError('The message left Trash, but could not be moved to Inbox. Refresh or check Gmail.', exc.status) from None
        return {'ok': True, 'restored': True}
    if data.get('action') == 'trash':
        gmail(email, 'messages/' + mid + '/trash', method='POST')
        return {'ok': True, 'trashed': True}
    actions = {'read': ([], ['UNREAD']), 'unread': (['UNREAD'], []),
               'star': (['STARRED'], []), 'unstar': ([], ['STARRED']), 'archive': ([], ['INBOX'])}
    if data.get('action') not in actions:
        raise MailError('Unsupported email action.')
    add, remove = actions[data['action']]
    gmail(email, 'messages/' + mid + '/modify', {'addLabelIds': add, 'removeLabelIds': remove})
    return {'ok': True}


def recipients(value):
    if not isinstance(value, str) or len(value) > 4000 or re.search(r'[\r\n\x00]', value):
        raise MailError('Enter valid recipient addresses.')
    parsed = getaddresses([value])
    if not parsed or len(parsed) > 50:
        raise MailError('Enter between 1 and 50 recipients.')
    for _, address in parsed:
        if not re.fullmatch(r'[^\s<>@,;]+@[^\s<>@,;]+\.[^\s<>@,;]+', address):
            raise MailError('Check the recipient email addresses.')
    return value


def send(data):
    email = email_address(data.get('account', ''))
    to = recipients(data.get('to', ''))
    subject = data.get('subject', '')
    text = data.get('body', '')
    if not isinstance(subject, str) or len(subject) > 998 or re.search(r'[\r\n\x00]', subject):
        raise MailError('Invalid subject.')
    if not isinstance(text, str) or not text.strip() or len(text.encode()) > 500000:
        raise MailError('Enter a message under 500 KB.')
    nonce = data.get('requestId', '')
    if not isinstance(nonce, str) or not re.fullmatch(r'[a-f0-9-]{36}', nonce):
        raise MailError('Invalid send request. Reopen Compose.')
    msg = EmailMessage(policy=SMTP)
    msg['From'], msg['To'], msg['Subject'] = email, to, subject
    msg.set_content(text)
    reply = data.get('replyId')
    payload = {}
    if reply:
        original = gmail(email, 'messages/' + item_id(reply) + '?format=metadata')
        message_id = header(original, 'message-id')
        if message_id and not re.search(r'[\r\n\x00]', message_id):
            msg['In-Reply-To'] = message_id
            msg['References'] = message_id
        payload['threadId'] = original['threadId']
    attachments = data.get('attachments', [])
    if not isinstance(attachments, list) or len(attachments) > 10:
        raise MailError('Choose at most 10 attachments.')
    total = 0
    for attachment in attachments:
        if not isinstance(attachment, dict):
            raise MailError('Invalid attachment.')
        name = attachment.get('name', '')
        if not isinstance(name, str) or not name or len(name) > 240 or re.search(r'[\r\n\x00/\\]', name):
            raise MailError('Invalid attachment filename.')
        try:
            raw = base64.b64decode(attachment['data'], validate=True)
        except (ValueError, KeyError, TypeError):
            raise MailError('Invalid attachment data.') from None
        total += len(raw)
        if total > 2000000:
            raise MailError('Attachments must total less than 2 MB.')
        msg.add_attachment(raw, maintype='application', subtype='octet-stream', filename=name)
    payload['raw'] = b64(msg.as_bytes())
    # Reserve the request before sending. Ambiguous failures must not resend automatically.
    with LOCK, database() as db:
        previous = db.execute('SELECT * FROM sent_requests WHERE request=?', (nonce,)).fetchone()
        if previous:
            if previous['email'] != email:
                raise MailError('Invalid send request.', 409)
            if previous['result']:
                return json.loads(previous['result'])
            raise MailError('This send was already attempted. Check Sent before composing another message.', 409)
        db.execute('INSERT INTO sent_requests VALUES (?,?,NULL,?)', (nonce, email, time.time()))
    result = gmail(email, 'messages/send', payload)
    answer = {'sent': True, 'id': result['id']}
    with database() as db:
        db.execute('UPDATE sent_requests SET result=? WHERE request=?', (json.dumps(answer), nonce))
    return answer


def attachment(query):
    email = email_address(query.get('account', ''))
    mid, aid = item_id(query.get('id')), item_id(query.get('attachment'))
    raw = gmail(email, 'messages/' + mid + '?format=full')
    _, parts = body_parts(raw.get('payload', {}))
    part = next((p for p in parts if p['id'] == aid), None)
    if not part:
        raise MailError('Attachment not found.', 404)
    if part['size'] > 2000000:
        raise MailError('Open Gmail to download attachments larger than 2 MB.', 413)
    result = gmail(email, 'messages/' + mid + '/attachments/' + aid)
    return {'name': part['name'], 'data': result['data']}


def disconnect(data):
    email = email_address(data.get('account', ''))
    with database() as db:
        db.execute('DELETE FROM accounts WHERE email=?', (email,))
    return {'disconnected': email}


def handle(method, path, query, data, session):
    if not re.fullmatch(r'[a-f0-9]{64}', session):
        raise MailError('Invalid workspace session.', 403)
    reads = {'status': lambda: status(), 'unread': lambda: unread(), 'messages': lambda: messages(query),
             'message': lambda: message(query), 'attachment': lambda: attachment(query)}
    writes = {'connect': lambda: connect(data, session), 'callback': lambda: callback(data, session),
              'modify': lambda: modify(data), 'send': lambda: send(data), 'disconnect': lambda: disconnect(data)}
    name = path.removeprefix('/api/mail/')
    fn = (reads if method == 'GET' else writes if method == 'POST' else {}).get(name)
    if not fn:
        raise MailError('Mail endpoint not found.', 404)
    return fn()
