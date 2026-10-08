import datetime as dt
import unittest
from unittest.mock import patch
import sports_odds as odds

DATE=dt.date(2026,10,8)
HTML='''<script type="application/ld+json">{"@type":"SportsEvent","identifier":1,"startDate":"2026-10-08T19:00:00-04:00","awayTeam":{"name":"UTA Mammoth"},"homeTeam":{"name":"BOS Bruins"}}</script><div class="event-card" id="nhl.1"><table><tr data-side="away"><td class="event-card-open"><span class="data-value">-999</span></td><td data-field="current-moneyline"><span class="data-value">+105</span></td><td data-field="current-total"><span class="data-value">o5.5</span><small class="data-odds">-110</small></td></tr><tr data-side="home"><td data-field="current-moneyline"><span class="data-value">-125</span></td><td data-field="current-spread"><span class="data-value">-1.5</span><small class="data-odds">+180</small></td></tr></table></div>'''
def event(**extra):return dict(id='x',state='pre',date='2026-10-08T23:00Z',teams=[{'name':'UTAH'},{'name':'BOS'}],**extra)

class OddsTests(unittest.TestCase):
    def test_current_cells_only_and_date_isolation(self):
        games=odds.parse_board(HTML,'NHL',DATE)
        self.assertEqual(games[0]['markets']['away']['moneyline'],'+105')
        self.assertEqual(games[0]['markets']['away']['total'],'o5.5 (-110)')
        self.assertEqual(odds.parse_board(HTML,'NHL',DATE+dt.timedelta(days=1)),[])
        with self.assertRaises(ValueError):odds.parse_board('<html>Maintenance</html>','NHL',DATE)

    def attach(self,games,stale=False,events=None):
        events=events or [event()]
        feed=dict(data=games,stale=stale,updatedAt='2026-10-08T12:00:00Z')
        with patch.object(odds.sports_page,'today',return_value=DATE),patch.object(odds,'board',return_value=feed):odds.attach(events,'NHL',DATE)
        return events[0]

    def test_match_uses_both_teams_and_start_time(self):
        games=odds.parse_board(HTML,'NHL',DATE)
        self.assertIsNotNone(self.attach(games)['odds']['markets'])
        games[0]['teams']['home']='TOR'
        self.assertIsNone(self.attach(games)['odds']['markets'])
        games[0]['teams']['home']='BOS';games[0]['start']='2026-10-08T21:00:00-04:00'
        self.assertIsNone(self.attach(games)['odds']['markets'])

    def test_ambiguous_games_stale_and_final_never_show_current_odds(self):
        games=odds.parse_board(HTML,'NHL',DATE)
        self.assertIsNone(self.attach(games*2)['odds']['markets'])
        self.assertIsNone(self.attach(games,stale=True)['odds']['markets'])
        final=event();final['state']='post'
        self.assertNotIn('odds',self.attach(games,events=[final]))

if __name__=='__main__':unittest.main()
