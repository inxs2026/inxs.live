#!/usr/bin/env python3
"""LAN dashboard. Read-only scheduler inventory; Python standard library only."""
import concurrent.futures
import news_summary
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import threading
import time
from zoneinfo import ZoneInfo
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import racing
import agco
import stocks
import stock_quotes
import woodbine_stats
import operations
import codex_usage
import performance
import sports_teams
import acknowledgements
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parent
HOME = Path.home()
CONFIG = json.loads((ROOT / 'config.json').read_text())
PORT = int(os.environ.get('DASHBOARD_PORT', '8088'))
HOST = os.environ.get('DASHBOARD_HOST', '10.0.0.49')
CACHE = ROOT / '.cache'
CACHE.mkdir(exist_ok=True)
LOCK = threading.Lock()
FEEDS = {}

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def command(*args):
    return subprocess.run(args, capture_output=True, text=True, timeout=12)

def properties(unit):
    result = command('systemctl', '--user', 'show', unit, '--no-pager')
    if result.returncode:
        raise RuntimeError('Could not inspect ' + unit)
    values = {}
    for line in result.stdout.splitlines():
        if '=' in line:
            k, v = line.split('=', 1)
            values.setdefault(k, []).append(v)
    return {k: '\n'.join(v) for k, v in values.items()}

def iso(value):
    if not value or value in ('n/a', '0', 'infinity'):
        return None
    try:
        # systemd emits local timezone abbreviations; the host's local zone handles DST.
        return dt.datetime.strptime(value.rsplit(' ', 1)[0], '%a %Y-%m-%d %H:%M:%S').astimezone().isoformat()
    except ValueError:
        return value

def platform(text):
    text = text.lower()
    h = '.hermes' in text or 'hermes-' in text
    o = '.openclaw' in text or 'openclaw' in text or 'charlie-pcloud' in text
    return 'Both' if h and o else 'OpenClaw' if o else 'Hermes'

def native_jobs(path, owner, archived=False):
    data = json.loads(path.read_text())
    return native_rows(data, owner, archived)

def native_rows(data, owner, archived=False):
    records = data if isinstance(data, list) else data.get('jobs', [])
    if not isinstance(records, list):
        raise ValueError('Invalid job registry')
    rows = []
    for j in records:
        schedule = j.get('schedule') or {}
        state = j.get('state') if isinstance(j.get('state'), dict) else {}
        enabled = j.get('enabled', True) and j.get('state') not in ('paused', 'completed', 'disabled') if not isinstance(j.get('state'), dict) else j.get('enabled', True)
        status = 'inactive' if archived or not enabled else 'active'
        kind = schedule.get('kind', 'unknown')
        display = j.get('schedule_display') or schedule.get('display') or schedule.get('expr') or schedule.get('at')
        if not display:
            display = 'Every ' + str(schedule.get('minutes', '?')) + ' minutes' if kind == 'interval' else 'Every ' + str(schedule.get('everyMs', 0) // 60000) + ' minutes' if kind == 'every' else 'Unspecified'
        rows.append(dict(id=owner + ':' + str(j.get('id')), name=j.get('name') or 'Unnamed job', platform=owner,
                         source='Migrated archive' if archived else owner + ' cron', status=status,
                         schedule=display, timezone=schedule.get('tz', 'America/Toronto'),
                         nextRun=None if archived else j.get('next_run_at') or (dt.datetime.fromtimestamp(state['nextRunAtMs']/1000, dt.timezone.utc).isoformat() if state.get('nextRunAtMs') else None),
                         lastRun=j.get('last_run_at') or (dt.datetime.fromtimestamp(state['lastRunAtMs']/1000, dt.timezone.utc).isoformat() if state.get('lastRunAtMs') else None),
                         result=j.get('last_status') or state.get('lastStatus') or 'unknown',
                         note='Historical definition. This registry is no longer used; replacement timers appear separately.' if archived else j.get('paused_reason') or '',
                         unit=str(j.get('id')), configured=bool(enabled), archived=archived,
                         deliveryStatus=state.get('lastDeliveryStatus') if isinstance(state, dict) else None,
                         failureReason=failure_reason(state.get('lastError') or j.get('last_error'))))
    return rows


def failure_reason(message):
    # Return fixed explanations only; scheduler errors can contain credentials or private paths.
    text = str(message or '').lower()
    if 'heartbeat failed: agent-runner-failure' in text:
        return 'The heartbeat agent could not complete its run.'
    if 'superseded' in text and 'runtime' in text:
        return 'The model runtime changed before the job could start.'
    if 'timeout' in text or 'timed out' in text:
        return 'The job exceeded its allowed time.'
    if 'rate limit' in text or '429' in text:
        return 'The provider temporarily limited requests.'
    if 'unauthorized' in text or 'authentication' in text or '401' in text:
        return 'The service could not authenticate.'
    if 'delivery' in text or 'telegram' in text:
        return 'The scheduler reported a delivery problem.'
    return None

def openclaw_jobs():
    # The gateway owns current schedules; jobs.json.migrated is historical only.
    binary = HOME / '.npm-global/bin/openclaw'
    result = command(str(binary), 'cron', 'list', '--all', '--json', '--timeout', '5000')
    if result.returncode:
        raise RuntimeError('OpenClaw live scheduler unavailable')
    data = json.loads(result.stdout)
    if not isinstance(data, dict) or not isinstance(data.get('jobs'), list) or data.get('hasMore'):
        raise ValueError('Incomplete OpenClaw scheduler inventory')
    return native_rows(data, 'OpenClaw')

def timer_jobs():
    result = command('systemctl', '--user', 'list-unit-files', '--type=timer', '--no-legend', '--no-pager')
    if result.returncode:
        raise RuntimeError('Timer inventory unavailable')
    names = [line.split()[0] for line in result.stdout.splitlines() if line and re.match(r'^(hermes-|openclaw-|myinxs-|nhl-daily|charlie-pcloud|lexi-pcloud|wo-staging)', line)]
    def read(unit):
        p = properties(unit)
        service = p.get('Unit') or unit.replace('.timer', '.service')
        s = properties(service)
        active = p.get('ActiveState') == 'active'
        schedule = re.findall(r'OnCalendar=(.*?)\s*;\s*next_elapse=', p.get('TimersCalendar', ''))
        schedule += re.findall(r'(On\w+Sec=.*?)\s*;', p.get('TimersMonotonic', ''))
        owner = platform(unit + ' ' + s.get('ExecStart', ''))
        note = 'Timer ' + p.get('UnitFileState', 'unknown') + ' · ' + p.get('ActiveState', 'unknown')
        if p.get('UnitFileState') == 'enabled' and not active:
            note += '. Enabled for startup, but currently not running.'
        return dict(id=unit, name=s.get('Description') or p.get('Description') or unit,
                    platform=owner, source='Linux timer', status='active' if active else 'inactive',
                    schedule='; '.join(schedule) or ('Masked — schedule unavailable' if p.get('UnitFileState') == 'masked' else 'No schedule available'),
                    timezone='America/Toronto', nextRun=iso(p.get('NextElapseUSecRealtime')) if active else None,
                    lastRun=iso(p.get('LastTriggerUSec')), result=s.get('Result', 'unknown') if p.get('LastTriggerUSec') and p.get('LastTriggerUSec') != 'n/a' else 'unknown',
                    note=note, unit=unit, configured=p.get('UnitFileState') == 'enabled', archived=False)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(read, names))

def crontab_jobs():
    proc = command('crontab', '-l')
    if proc.returncode and 'no crontab' not in proc.stderr:
        raise RuntimeError('Crontab unavailable')
    rows = []
    zone = 'America/Toronto'
    for line in proc.stdout.splitlines():
        if line.startswith('CRON_TZ='):
            zone = line.split('=', 1)[1].strip()
        inactive = line.lstrip().startswith('#')
        value = line.lstrip().lstrip('#').strip()
        match = re.match(r'^((?:[\d*/?,\-]+\s+){4}[\d*/?,\-]+|@(?:reboot|yearly|annually|monthly|weekly|daily|hourly))\s+(.+)$', value)
        if not match or not any(t in match[2] for t in ('.hermes', '.openclaw', 'hermes', 'openclaw')):
            continue
        cmd = match[2]
        scripts = re.findall(r'/[^\s>]+\.(?:py|sh)', cmd)
        name = Path(scripts[-1]).stem.replace('_', ' ').replace('-', ' ').title() if scripts else 'Agent crontab task'
        rows.append(dict(id='crontab:' + hashlib.sha256(value.encode()).hexdigest()[:12], name=name, platform=platform(cmd),
                         source='System crontab', status='inactive' if inactive else 'active', schedule=match[1], timezone=zone,
                         nextRun=None, lastRun=None, result='unknown', note='Direct cron schedule. Next-run and execution history are not provided by crontab.',
                         unit=scripts[-1] if scripts else 'crontab', configured=not inactive, archived=False))
    return rows

def inventory():
    rows, sources, errors = [], [], []
    for owner in ('Hermes', 'OpenClaw'):
        try:
            jobs = openclaw_jobs() if owner == 'OpenClaw' else native_jobs(HOME / '.hermes/cron/jobs.json', owner)
            rows.extend(jobs)
            sources.append(dict(name=owner + ' registry', ok=True, count=len(jobs), note='Live gateway scheduler' if owner == 'OpenClaw' else 'Live registry'))
        except Exception:
            sources.append(dict(name=owner + ' registry', ok=False, count=0, note='Unavailable'))
            errors.append(owner + ' registry could not be read')
    for path in sorted((HOME / '.hermes/profiles').glob('*/cron/jobs.json')):
        profile = path.parent.parent.name
        try:
            jobs = native_jobs(path, 'Hermes')
            for job in jobs:
                job['id'] = 'Hermes:' + profile + ':' + job['unit']
                job['source'] = 'Hermes profile cron'
                job['note'] = ('Profile: ' + profile + '. ' + job['note']).strip()
            rows.extend(jobs)
            sources.append(dict(name='Hermes profile: ' + profile, ok=True, count=len(jobs), note='Profile registry'))
        except Exception:
            sources.append(dict(name='Hermes profile: ' + profile, ok=False, count=0, note='Unavailable'))
            errors.append('Hermes profile registry could not be read: ' + profile)
    archive = HOME / '.openclaw/cron/jobs.json.migrated'
    if archive.exists():
        try:
            live_ids = {j['id'] for j in rows}
            jobs = [j for j in native_jobs(archive, 'OpenClaw', True) if j['id'] not in live_ids]
            rows.extend(jobs)
            sources.append(dict(name='OpenClaw migrated archive', ok=True, count=len(jobs), note='Historical definitions absent from live scheduler'))
        except Exception:
            sources.append(dict(name='OpenClaw migrated archive', ok=False, count=0, note='Unavailable'))
            errors.append('OpenClaw migrated archive could not be read')
    for name, reader in [('Linux timers', timer_jobs), ('System crontab', crontab_jobs)]:
        try:
            jobs = reader()
            rows.extend(jobs)
            sources.append(dict(name=name, ok=True, count=len(jobs), note='Live schedules'))
        except Exception:
            sources.append(dict(name=name, ok=False, count=0, note='Unavailable'))
            errors.append(name + ' could not be read')
    gateways = {}
    for owner in ('Hermes', 'OpenClaw'):
        proc = command('systemctl', '--user', 'is-active', owner.lower() + '-gateway.service')
        gateways[owner] = proc.stdout.strip() or 'unknown'
    rows.sort(key=lambda j: (j['status'] != 'active', j['archived'], j['platform'], j['name']))
    return dict(jobs=rows, sources=sources, errors=errors, gateways=gateways, updatedAt=now(), timezone='America/Toronto')

def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'LocalDashboard/1.0 (personal RSS reader)'})
    with urllib.request.urlopen(request, timeout=15) as r:
        return r.read(2_000_000)

def weather():
    city = CONFIG['weather']
    query = urllib.parse.urlencode(dict(latitude=city['latitude'], longitude=city['longitude'], current='temperature_2m,apparent_temperature,weather_code,wind_speed_10m', daily='temperature_2m_max,temperature_2m_min', timezone='America/Toronto', forecast_days=5))
    data = json.loads(fetch('https://api.open-meteo.com/v1/forecast?' + query))
    return dict(city=city['name'], current=data['current'], daily=data['daily'], source='Open-Meteo', url='https://open-meteo.com/')

def headlines(kind):
    options = CONFIG[kind + 'Feeds']
    for option in options:
        try:
            root = ET.fromstring(fetch(option['url']))
            items = []
            for item in root.findall('./channel/item')[:6]:
                link = item.findtext('link') or ''
                if urllib.parse.urlparse(link).scheme not in ('http', 'https'):
                    continue
                description = news_summary.summary(item.findtext('description') or item.findtext('{http://purl.org/rss/1.0/modules/content/}encoded'))
                if not description and kind in ('news', 'usnews') and len(items) < 4:
                    try:
                        description = news_summary.article_summary(fetch(link).decode('utf-8', 'replace'))
                    except Exception:
                        pass
                items.append(dict(title=item.findtext('title') or 'Headline', url=link, published=item.findtext('pubDate'), source=option['name'], summary=description))
            if items:
                return dict(items=items, source=option['name'], url=option['url'])
        except Exception:
            continue
    raise RuntimeError('Feeds unavailable')

def scores():
    target = dt.datetime.now(ZoneInfo('America/Toronto')).date()
    leagues = [('NHL', 'hockey/nhl'), ('MLB', 'baseball/mlb'), ('NFL', 'football/nfl')]
    results = []
    failed = []
    def league(pair):
        name, slug = pair
        data = json.loads(fetch('https://site.api.espn.com/apis/site/v2/sports/' + slug + '/scoreboard?dates=' + target.strftime('%Y%m%d') + '&limit=1000'))
        brands=sports_teams.registry(slug)
        events = []
        for event in data.get('events', []):
            if dt.datetime.fromisoformat(event['date'].replace('Z', '+00:00')).astimezone(ZoneInfo('America/Toronto')).date() != target:
                continue
            competition = event['competitions'][0]
            teams = sorted(competition['competitors'], key=lambda c: c.get('homeAway') == 'home')
            events.append(dict(id=event['id'], date=event['date'], status=event['status']['type']['shortDetail'], state=event['status']['type']['state'], teams=[sports_teams.competitor(t,brands) for t in teams], url='https://www.espn.com/' + slug + '/game/_/gameId/' + event['id']))
        return dict(league=name, logo=sports_teams.branding((data.get('leagues') or [{}])[0])['logo'], events=events)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(league, pair): pair[0] for pair in leagues}
        for f, name in futures.items():
            try:
                results.append(f.result())
            except Exception:
                failed.append(name)
    if not results:
        raise RuntimeError('Scoreboards unavailable')
    return dict(date=target.isoformat(), leagues=results, unavailable=failed, source='ESPN', url='https://www.espn.com/')

def update_feed(name, reader):
    try:
        value = dict(data=reader(), updatedAt=now(), stale=False, error=None)
        temp = CACHE / (name + '.tmp')
        temp.write_text(json.dumps(value))
        temp.replace(CACHE / (name + '.json'))
    except Exception:
        with LOCK:
            value = dict(FEEDS.get(name, dict(data=None, updatedAt=None)))
        value.update(stale=True, error='Temporarily unavailable. Retrying automatically.')
    with LOCK:
        FEEDS[name] = value

def feed_worker():
    for name in ('weather', 'news', 'usnews', 'sports', 'scores'):
        try:
            value = json.loads((CACHE / (name + '.json')).read_text())
            value['stale'] = True
            FEEDS[name] = value
        except Exception:
            FEEDS[name] = dict(data=None, updatedAt=None, stale=False, error=None)
    while True:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            tasks = [pool.submit(update_feed, name, reader) for name, reader in [('weather', weather), ('news', lambda: headlines('news')), ('usnews', lambda: headlines('usnews')), ('sports', lambda: headlines('sports')), ('scores', scores)]]
            for task in tasks:
                task.result()
        time.sleep(600)

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        path=urllib.parse.urlparse(self.path).path
        if path!='/api/acknowledgements':return self.send_error(405)
        try:
            origin=urllib.parse.urlsplit(self.headers.get('Origin',''))
            if origin.netloc!=self.headers.get('Host'):return self.send_error(403)
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=65536:raise ValueError('Invalid body')
            form=urllib.parse.parse_qs(self.rfile.read(length).decode(),strict_parsing=True)
            result=acknowledgements.observe(json.loads(form['notices'][0]),form.get('complete',['false'])[0]=='true') if 'notices' in form else acknowledgements.acknowledge(form.get('key',[''])[0])
            self.respond(json.dumps(result).encode(),'application/json')
        except (ValueError,UnicodeError):self.send_error(400)
        except Exception:self.send_error(503)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path in ('/cameras','/cameras/'):
            self.send_response(302)
            self.send_header('Location','https://inxs.live/cameras')
            self.send_header('Cache-Control','no-store')
            self.end_headers()
        elif path == '/api/acknowledgements':
            self.respond(json.dumps(acknowledgements.listing()).encode(),'application/json')
        elif path == '/api/jobs':
            self.respond(json.dumps(inventory()).encode(), 'application/json')
        elif path == '/api/codex-usage':
            self.respond(json.dumps(codex_usage.usage()).encode(), 'application/json')
        elif path == '/api/system-health':
            self.respond(json.dumps(operations.system_health()).encode(), 'application/json')
        elif path == '/api/timeline':
            self.respond(json.dumps(operations.timeline(inventory())).encode(), 'application/json')
        elif path == '/api/racing-performance':
            self.respond(json.dumps(performance.build()).encode(), 'application/json')
        elif path == '/api/racing':
            try:
                query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                self.respond(json.dumps(racing.build(query.get('date', [None])[0])).encode(), 'application/json')
            except ValueError:
                self.send_error(400, 'Invalid race date or unavailable card')
        elif path == '/agco-document':
            try:
                query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                file = agco.document_path(query.get('kind', [''])[0], query.get('date', [''])[0])
                if file and file.read_bytes()[:5] == b'%PDF-':
                    self.respond(file.read_bytes(), 'application/pdf')
                else:
                    self.send_error(404, 'Report is not available')
            except ValueError:
                self.send_error(400, 'Invalid AGCO report request')
        elif path == '/racing-document':
            try:
                query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                file = racing.document_path(query.get('agent', [''])[0], query.get('date', [''])[0])
                if file and file.read_bytes()[:5] == b'%PDF-':
                    self.respond(file.read_bytes(), 'application/pdf')
                else:
                    self.send_error(404, 'Report is not available')
            except ValueError:
                self.send_error(400, 'Invalid report request')
        elif path == '/api/woodbine-stats':
            self.respond(json.dumps(woodbine_stats.build()).encode(), 'application/json')
        elif path == '/stats-document':
            try:
                query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                file = woodbine_stats.document_path(query.get('report', [''])[0])
                if file and file.is_file() and file.read_bytes()[:5] == b'%PDF-':
                    self.respond(file.read_bytes(), 'application/pdf')
                else:
                    self.send_error(404, 'Report is not available')
            except ValueError:
                self.send_error(400, 'Invalid report request')
        elif path == '/api/stocks':
            self.respond(json.dumps(stocks.build()).encode(), 'application/json')
        elif path == '/api/stock-quotes':
            self.respond(json.dumps(stock_quotes.build()).encode(), 'application/json')
        elif path == '/stock-document':
            try:
                query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                file = stocks.document_path(query.get('report', [''])[0])
                if file and file.read_bytes()[:5] == b'%PDF-':
                    self.respond(file.read_bytes(), 'application/pdf')
                else:
                    self.send_error(404, 'Report is not available')
            except ValueError:
                self.send_error(400, 'Invalid report request')
        elif path == '/api/briefing':
            with LOCK:
                data = dict(FEEDS)
            self.respond(json.dumps(data).encode(), 'application/json')
        elif path == '/api/health':
            self.respond(json.dumps(dict(status='ok', time=now())).encode(), 'application/json')
        elif path in ('/', '/health', '/health/', '/operations.js', '/operations.css', '/stocks', '/stocks/', '/briefing', '/briefing/', '/woodbine', '/woodbine/', '/woodbine-stats', '/woodbine-stats/', '/stats.js', '/stats.css', '/app.js', '/team-branding.js', '/attention.js', '/stocks.js', '/stocks.css', '/racing.js', '/racing.css', '/style.css', '/mobile.css', '/pages.css', '/favicon.svg'):
            name = {'/': 'index.html', '/health': 'health.html', '/health/': 'health.html', '/stocks': 'stocks.html', '/stocks/': 'stocks.html', '/briefing': 'briefing.html', '/briefing/': 'briefing.html', '/woodbine': 'woodbine.html', '/woodbine/': 'woodbine.html', '/woodbine-stats': 'woodbine-stats.html', '/woodbine-stats/': 'woodbine-stats.html'}.get(path, path[1:])
            types = {'.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css', '.svg': 'image/svg+xml'}
            self.respond((ROOT / 'static' / name).read_bytes(), types[Path(name).suffix])
        else:
            self.send_error(404)

    def respond(self, body, content_type):
        self.send_response(200)
        self.send_header('Content-Type', content_type + ('; charset=utf-8' if content_type != 'application/pdf' else ''))
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' https://a.espncdn.com; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    threading.Thread(target=feed_worker, daemon=True).start()
    threading.Thread(target=stock_quotes.worker, daemon=True).start()
    print(f'Dashboard listening on http://{HOST}:{PORT}', flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
