import datetime as dt
import unittest
from unittest.mock import patch
import sports_page
class SportsTests(unittest.TestCase):
 def setUp(self):sports_page.CACHE.clear();sports_page.KEY_LOCKS.clear()
 def test_past_and_future_dates_stay_separate(self):
  with patch.object(sports_page,'today',return_value=dt.date(2026,10,7)):
   for value in ['2026-10-06','2026-10-07','2026-10-08','2027-01-01']:
    r=sports_page.scoreboard(value,lambda date:{'date':date.isoformat()});self.assertEqual(r['data']['date'],value)
   for value in ['bad','1999-12-31','2100-01-01']:
    with self.assertRaises(ValueError):sports_page.date_value(value)
 def test_season_selection_does_not_use_future_baseball_season(self):
  date=dt.date(2026,10,7)
  self.assertEqual(sports_page.season_year('MLB',date),2026);self.assertEqual(sports_page.season_year('NHL',date),2027)
  self.assertEqual(sports_page.season_year('NFL',dt.date(2027,1,10)),2026)
 def test_failed_refresh_is_labeled_stale_and_keeps_last_date(self):
  sports_page.cached('fixture',lambda:{'date':'2026-10-06'},0)
  def fail():raise RuntimeError('Unavailable')
  result=sports_page.cached('fixture',fail,0);self.assertTrue(result['stale']);self.assertEqual(result['data']['date'],'2026-10-06');self.assertIsNotNone(result['error'])
 def test_nested_groups_keep_team_branding_and_missing_stats(self):
  data={'season':{'displayName':'2026'},'children':[{'name':'AFC','children':[{'name':'East','standings':{'entries':[{'team':{'id':'1','abbreviation':'BUF'},'stats':[{'name':'wins','displayValue':'3'}]}]}}]}]}
  result=sports_page.normalize_standings('NFL',data,{'1':{'logo':'https://a.espncdn.com/team.png','color':'#123456','displayName':'Buffalo Bills'}})
  row=result['groups'][0]['rows'][0];self.assertEqual(row['team']['displayName'],'Buffalo Bills');self.assertEqual(row['stats']['wins'],'3');self.assertNotIn('losses',row['stats'])
  with self.assertRaises(ValueError):sports_page.normalize_standings('NFL',{}, {})
if __name__=='__main__':unittest.main()
