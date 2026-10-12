import datetime as dt
import unittest
import io,json
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
 def test_standings_request_keeps_full_stats_not_alternate_split_view(self):
  data={'season':{'displayName':'2026-27'},'children':[{'name':'Eastern','standings':{'entries':[{'team':{'id':'1','abbreviation':'TOR'},'stats':[{'name':'pointsFor','displayValue':'16'},{'name':'pointsAgainst','displayValue':'8'},{'name':'Home','displayValue':'3-0-0'}]}]}}]}
  with patch.object(sports_page,'today',return_value=dt.date(2026,10,7)),patch.object(sports_page.sports_teams,'registry',return_value={}),patch.object(sports_page.urllib.request,'urlopen',return_value=io.BytesIO(json.dumps(data).encode())) as request:
   result=sports_page.standings('NHL');url=request.call_args.args[0].full_url
   self.assertIn('season=2027',url);self.assertNotIn('&type=',url)
   stats=result['data']['groups'][0]['rows'][0]['stats'];self.assertEqual(stats['pointsFor'],'16');self.assertEqual(stats['pointsAgainst'],'8');self.assertEqual(stats['Home'],'3-0-0')
 def test_playoff_series_uses_provider_status_and_expands_team_name(self):
  game={'series':{'type':'playoff','summary':'CHW lead series 2-0'},'competitors':[{'team':{'abbreviation':'CHW','shortDisplayName':'White Sox'}}]}
  self.assertEqual(sports_page.playoff_series(game),'White Sox lead series 2-0')
  for summary in ['Series tied 1-1','CHW win series 3-0']:
   game['series']['summary']=summary;self.assertEqual(sports_page.playoff_series(game),summary.replace('CHW','White Sox'))
  game['series']['type']='regular-season';self.assertIsNone(sports_page.playoff_series(game))
  self.assertIsNone(sports_page.playoff_series({}))
  self.assertIsNone(sports_page.playoff_series({'series':{'type':'playoff'}}))
class StandingsViewTests(unittest.TestCase):
 def test_mlb_feed_order_does_not_put_division_leader_last(self):
  entries=[{'team':{'id':str(i),'abbreviation':name},'stats':[{'name':'winPercent','value':pct,'displayValue':str(pct)},{'name':'playoffSeed','value':seed}]} for i,(name,pct,seed) in enumerate([('NYY',.578,4),('BOS',.537,5),('TB',.605,1)])]
  data={'children':[{'name':'American League','children':[{'name':'AL East','standings':{'entries':entries}}]}]}
  result=sports_page.standings_views(sports_page.normalize_standings('MLB',data,{}))
  self.assertEqual([r['team']['name'] for r in result['views']['american'][0]['rows']],['TB','NYY','BOS'])
  self.assertEqual(result['views']['wildcard'][0]['rows'][0]['team']['name'],'TB')
  self.assertEqual([r['team']['name'] for r in result['views']['wildcard'][1]['rows']],['NYY','BOS'])
 def test_nfl_postseason_belongs_to_following_calendar_year(self):
  with patch.object(sports_page,'today',return_value=dt.date(2026,10,12)),patch.object(sports_page.urllib.request,'urlopen') as request:
   self.assertEqual(sports_page.postseason('NFL',2026,{}),[]);request.assert_not_called()
if __name__=='__main__':unittest.main()
