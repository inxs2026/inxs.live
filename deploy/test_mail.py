import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
import inxs_mail as mail


class MailTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.state = patch.object(mail, 'STATE', Path(self.temp.name) / 'state')
        self.state.start()
        self.client = patch.object(mail, 'config', return_value={'client_id': 'fixture', 'client_secret': 'fixture-secret'})
        self.client.start()

    def tearDown(self):
        self.state.stop()
        self.client.stop()
        self.temp.cleanup()

    def test_status_never_exposes_tokens(self):
        with mail.database() as db:
            db.execute('INSERT INTO accounts VALUES (?,?,?,?,?)', ('lexiinxs@gmail.com', 'refresh-secret', 'access-secret', time.time()+3600, time.time()))
        result = mail.status()
        self.assertEqual(result['accounts'][0]['email'], 'lexiinxs@gmail.com')
        self.assertNotIn('secret', json.dumps(result))
        self.assertEqual((mail.STATE / 'mail.sqlite3').stat().st_mode & 0o777, 0o600)

    def test_missing_configuration_is_not_a_connected_mailbox(self):
        with patch.object(mail, 'config', return_value=None):
            self.assertEqual(mail.unread(), {'connected': False, 'configured': False, 'unread': None})
            with self.assertRaises(mail.MailError):
                mail.connect({}, 'a'*64)

    def test_connect_uses_pkce_fixed_callback_and_scope(self):
        from urllib.parse import urlsplit, parse_qs
        result = mail.connect({}, 'a'*64)
        params = parse_qs(urlsplit(result['url']).query)
        self.assertEqual(params['redirect_uri'], [mail.CALLBACK])
        self.assertEqual(params['scope'], [mail.SCOPE])
        self.assertEqual(params['code_challenge_method'], ['S256'])
        self.assertEqual(params['login_hint'], ['lexiinxs@gmail.com'])

    def pending(self):
        from urllib.parse import urlsplit, parse_qs
        return parse_qs(urlsplit(mail.connect({}, 'a'*64)['url']).query)['state'][0]

    def test_callback_is_bound_to_session_and_single_use(self):
        state = self.pending()
        with patch.object(mail, 'request_json') as external:
            with self.assertRaises(mail.MailError):
                mail.callback({'state':state, 'code':'fixture'}, 'b'*64)
            external.assert_not_called()
        with self.assertRaises(mail.MailError):
            mail.callback({'state':state, 'error':'access_denied'}, 'a'*64)
        with self.assertRaises(mail.MailError):
            mail.callback({'state':state, 'code':'fixture'}, 'a'*64)

    def test_callback_rejects_different_google_account(self):
        state = self.pending()
        with patch.object(mail, 'request_json', return_value={'access_token':'fixture', 'scope':mail.SCOPE}), patch.object(mail, 'gmail', return_value={'emailAddress':'wrong@gmail.com'}):
            with self.assertRaises(mail.MailError):
                mail.callback({'state':state, 'code':'fixture'}, 'a'*64)
        self.assertEqual(mail.status()['accounts'], [])

    def test_callback_saves_only_after_scope_and_profile_validation(self):
        state = self.pending()
        with patch.object(mail, 'request_json', return_value={'access_token':'fixture', 'refresh_token':'refresh', 'scope':mail.SCOPE}), patch.object(mail, 'gmail', return_value={'emailAddress':'lexiinxs@gmail.com'}):
            self.assertEqual(mail.callback({'state':state, 'code':'fixture'}, 'a'*64), {'connected':'lexiinxs@gmail.com'})
        self.assertEqual(len(mail.status()['accounts']), 1)

    def test_html_is_reduced_to_text_without_scripts_or_remote_images(self):
        payload = {'mimeType':'text/html', 'body':{'data':mail.b64(b'<head><style>bad</style></head><p>Hello</p><script>steal()</script><img src="https://tracker.invalid/pixel"><p>World</p>')}}
        text, attachments = mail.body_parts(payload)
        self.assertIn('Hello', text)
        self.assertIn('World', text)
        self.assertNotIn('steal', text)
        self.assertNotIn('tracker', text)
        self.assertNotIn('bad', text)
        self.assertEqual(attachments, [])

    def test_plain_text_preferred_over_html_and_attachments_not_rendered(self):
        payload = {'parts':[{'mimeType':'text/plain','body':{'data':mail.b64(b'plain')}},{'mimeType':'text/html','body':{'data':mail.b64(b'<p>html</p>')}},{'filename':'invoice.pdf','body':{'attachmentId':'abc','size':50}}]}
        text, attachments = mail.body_parts(payload)
        self.assertEqual(text, 'plain')
        self.assertEqual(attachments[0]['name'], 'invoice.pdf')

    def send_data(self):
        return {'account':'lexiinxs@gmail.com','to':'friend@example.com','subject':'Hello','body':'Fixture only','requestId':'12345678-1234-1234-1234-123456789abc'}

    def test_header_injection_is_rejected_without_provider_request(self):
        for key,value in [('to','friend@example.com\r\nBcc: bad@example.com'),('subject','Hi\r\nBcc: bad@example.com')]:
            data=self.send_data();data[key]=value
            with patch.object(mail,'gmail') as external:
                with self.assertRaises(mail.MailError):
                    mail.send(data)
                external.assert_not_called()

    def test_successful_send_idempotency(self):
        with patch.object(mail,'gmail',return_value={'id':'sent-id'}) as external:
            first=mail.send(self.send_data())
            self.assertEqual(mail.send(self.send_data()),first)
            self.assertEqual(external.call_count,1)
            payload=external.call_args.args[2]
            decoded=mail.unb64(payload['raw']).decode()
            self.assertIn('From: lexiinxs@gmail.com',decoded)
            self.assertIn('To: friend@example.com',decoded)

    def test_ambiguous_send_failure_cannot_automatically_send_twice(self):
        with patch.object(mail,'gmail',side_effect=mail.MailError('Network unavailable',502)) as external:
            with self.assertRaises(mail.MailError):mail.send(self.send_data())
            with self.assertRaisesRegex(mail.MailError,'Check Sent'):mail.send(self.send_data())
            self.assertEqual(external.call_count,1)

    def test_attachment_size_limit_before_sending(self):
        data=self.send_data();data['attachments']=[{'name':'large.bin','data':mail.base64.b64encode(b'x'*2000001).decode()}]
        with patch.object(mail,'gmail') as external:
            with self.assertRaises(mail.MailError):mail.send(data)
            external.assert_not_called()

    def test_unread_failure_never_looks_like_zero(self):
        with patch.object(mail,'status',return_value={'configured':True,'accounts':[{'email':'lexiinxs@gmail.com'}]}), patch.object(mail,'gmail',side_effect=mail.MailError('Unavailable')):
            self.assertIsNone(mail.unread()['unread'])

    def test_unread_counts_all_connected_mailboxes(self):
        with patch.object(mail,'status',return_value={'configured':True,'accounts':[{'email':'lexiinxs@gmail.com'},{'email':'other@gmail.com'}]}), patch.object(mail,'gmail',return_value={'messagesUnread':3}):
            self.assertEqual(mail.unread()['unread'],6)

    def test_trash_uses_recoverable_endpoint_with_empty_post(self):
        with patch.object(mail,'gmail',return_value={'id':'abc','labelIds':['TRASH']}) as external:
            result=mail.modify({'account':'lexiinxs@gmail.com','id':'abc','action':'trash'})
            external.assert_called_once_with('lexiinxs@gmail.com','messages/abc/trash',method='POST')
            self.assertEqual(result,{'ok':True,'trashed':True})

    def test_trash_failure_is_not_reported_as_success(self):
        with patch.object(mail,'gmail',side_effect=mail.MailError('Google unavailable',502)):
            with self.assertRaises(mail.MailError):
                mail.modify({'account':'lexiinxs@gmail.com','id':'abc','action':'trash'})

    def test_trash_rejects_path_injection_before_calling_google(self):
        with patch.object(mail,'gmail') as external:
            with self.assertRaises(mail.MailError):
                mail.modify({'account':'lexiinxs@gmail.com','id':'../abc','action':'trash'})
            external.assert_not_called()

    def test_trash_listing_includes_trash_but_keeps_its_label_filter(self):
        from urllib.parse import urlsplit, parse_qs
        with patch.object(mail,'access_token',return_value='fixture'), patch.object(mail,'gmail',return_value={'messages':[]}) as external:
            mail.messages({'account':'lexiinxs@gmail.com','folder':'TRASH','q':'sample','page':'page-two'})
            query=parse_qs(urlsplit(external.call_args.args[1]).query)
            self.assertEqual(query['labelIds'],['TRASH'])
            self.assertEqual(query['includeSpamTrash'],['true'])
            self.assertEqual(query['q'],['sample'])
            self.assertEqual(query['pageToken'],['page-two'])

    def test_normal_inbox_does_not_include_trash(self):
        with patch.object(mail,'access_token',return_value='fixture'), patch.object(mail,'gmail',return_value={'messages':[]}) as external:
            mail.messages({'account':'lexiinxs@gmail.com','folder':'INBOX'})
            self.assertNotIn('includeSpamTrash',external.call_args.args[1])

    def test_restore_untrashes_and_explicitly_moves_to_inbox(self):
        from unittest.mock import call
        with patch.object(mail,'gmail',return_value={'id':'abc'}) as external:
            result=mail.modify({'account':'lexiinxs@gmail.com','id':'abc','action':'restore'})
            self.assertEqual(external.call_args_list,[
                call('lexiinxs@gmail.com','messages/abc/untrash',method='POST'),
                call('lexiinxs@gmail.com','messages/abc/modify',{'addLabelIds':['INBOX'],'removeLabelIds':['SPAM']})])
            self.assertEqual(result,{'ok':True,'restored':True})

    def test_failed_untrash_does_not_add_inbox_or_claim_restored(self):
        with patch.object(mail,'gmail',side_effect=mail.MailError('Unavailable',502)) as external:
            with self.assertRaises(mail.MailError):
                mail.modify({'account':'lexiinxs@gmail.com','id':'abc','action':'restore'})
            self.assertEqual(external.call_count,1)

    def test_partial_restore_reports_what_actually_happened(self):
        with patch.object(mail,'gmail',side_effect=[{'id':'abc'},mail.MailError('Unavailable',502)]):
            with self.assertRaisesRegex(mail.MailError,'message left Trash'):
                mail.modify({'account':'lexiinxs@gmail.com','id':'abc','action':'restore'})

    def test_paths_and_actions_are_allowlisted(self):
        with self.assertRaises(mail.MailError):mail.handle('GET','/api/mail/status',{}, {},'')
        with self.assertRaises(mail.MailError):mail.handle('POST','/api/mail/status',{}, {},'a'*64)
        with self.assertRaises(mail.MailError):mail.item_id('../secrets')
        with self.assertRaises(mail.MailError):mail.modify({'account':'lexiinxs@gmail.com','id':'abc','action':'delete-forever'})


if __name__ == '__main__':
    unittest.main()
