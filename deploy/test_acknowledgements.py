import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
import acknowledgements as a
class AcknowledgementsTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.mock=patch.object(a,'DB',Path(self.folder.name)/'state.db');self.mock.start()
    def tearDown(self):self.mock.stop();self.folder.cleanup()
    def notice(self,key):return dict(key=key,text='Test failure',url='/dashboard')
    def test_acknowledgement_persists_but_new_run_alerts(self):
        a.observe([self.notice('job1|oct4')],True);a.acknowledge('job1|oct4');a.acknowledge('job1|oct4')
        self.assertEqual(a.listing()['keys'],['job1|oct4'])
        a.observe([self.notice('job1|oct8')],True)
        result=a.listing();self.assertEqual(result['keys'],[]);self.assertEqual(len(result['history']),2)
        self.assertIsNotNone(result['history'][1]['acknowledged_at']);self.assertIsNotNone(result['history'][1]['resolved_at'])
    def test_recovery_rearms_same_issue_and_retains_history(self):
        a.observe([self.notice('feed')],True);a.acknowledge('feed');a.observe([],True);a.observe([self.notice('feed')],True)
        self.assertEqual(a.listing()['keys'],[]);self.assertEqual(len(a.listing()['history']),2)
    def test_partial_check_does_not_clear_unobserved_issue(self):
        a.observe([self.notice('job')],True);a.acknowledge('job');a.observe([],False)
        self.assertEqual(a.listing()['keys'],['job'])
    def test_verification_is_distinct_from_acknowledgement(self):
        a.observe([self.notice('job')],True);a.verify('job','Startup test passed')
        self.assertEqual(a.listing()['keys'],[]);self.assertEqual(a.listing()['history'][0]['verification'],'Startup test passed')
    def test_invalid_inputs(self):
        for value in ['',None,'a'*2049,'a\nb']:
            with self.assertRaises(ValueError):a.acknowledge(value)
        with self.assertRaises(ValueError):a.observe([dict(key='job',text='Test',url='https://outside.example')])
