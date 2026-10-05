import datetime as dt
import json
import unittest
from unittest.mock import patch
import server


class ScoreboardTests(unittest.TestCase):
    def test_all_games_and_toronto_day_boundary(self):
        class Clock(dt.datetime):
            @classmethod
            def now(cls, tz=None):
                return cls(2026,10,4,21,tzinfo=server.ZoneInfo('America/Toronto'))
        def event(i, date):
            return dict(id=str(i),date=date,status={'type':{'shortDetail':'Final','state':'post'}},
                        competitions=[{'competitors':[dict(homeAway=side,score='3',team={'abbreviation':'TEAM','displayName':'Team'}) for side in ('away','home')]}])
        # Includes a late Toronto game whose UTC timestamp falls on Monday.
        events=[event(i,'2026-10-04T17:00:00Z') for i in range(14)]
        events += [event(14,'2026-10-05T00:20:00Z'),event(15,'2026-10-05T17:00:00Z')]
        with patch.object(server.dt,'datetime',Clock),patch.object(server.sports_teams,'registry',return_value={}),patch.object(server,'fetch',return_value=json.dumps({'events':events}).encode()) as fetch:
            data=server.scores()
        self.assertEqual(data['date'],'2026-10-04')
        self.assertEqual([len(l['events']) for l in data['leagues']],[15,15,15])
        self.assertTrue(all('dates=20261004&limit=1000' in call.args[0] for call in fetch.call_args_list))


if __name__=='__main__':unittest.main()
