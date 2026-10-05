import unittest
from unittest.mock import patch
import codex_usage as c
class UsageTests(unittest.TestCase):
 def setUp(self):c.SNAPSHOT=None;c.CHECKED=0
 def test_multiple_buckets_and_remaining(self):
  rows=c.normalize({'rateLimitsByLimitId':{'codex':{'primary':{'usedPercent':25,'windowDurationMins':300,'resetsAt':1791230000},'secondary':{'usedPercent':90,'windowDurationMins':10080}},'other':{'primary':{'usedPercent':12}}},'rateLimits':{'primary':{'usedPercent':99}}})
  self.assertEqual(len(rows),3);self.assertEqual(rows[0]['remainingPercent'],75);self.assertEqual(rows[1]['remainingPercent'],10)
 def test_unknown_values_and_credentials_are_not_forwarded(self):
  rows=c.normalize({'rateLimits':{'primary':{'usedPercent':None},'secondary':{'usedPercent':float('nan')},'access_token':'secret'}})
  self.assertTrue(all(r['remainingPercent'] is None for r in rows));self.assertNotIn('secret',str(rows))
 def test_cache_and_failed_refresh_retain_original_timestamp(self):
  with patch.object(c,'read_limits',return_value={'state':'current','windows':[{'remainingPercent':70}],'note':'Current'}) as read:
   first=c.usage();self.assertEqual(c.usage(),first);self.assertEqual(read.call_count,1)
  c.CHECKED=0
  with patch.object(c,'read_limits',side_effect=TimeoutError()):
   stale=c.usage();self.assertEqual(stale['state'],'cached');self.assertEqual(stale['fetchedAt'],first['fetchedAt'])
 def test_signin_required_does_not_show_old_quota(self):
  c.SNAPSHOT={'state':'current','windows':[{'remainingPercent':70}]}
  with patch.object(c,'read_limits',return_value={'state':'signin-required','windows':[],'note':'Reconnect'}):self.assertEqual(c.usage()['windows'],[])
if __name__=='__main__':unittest.main()
