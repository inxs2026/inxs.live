import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import woodbine_stats as stats

class FixedDatetime(dt.datetime):
    @classmethod
    def now(cls,tz=None):return cls(2026,10,25,12,tzinfo=tz)

class HandleYTDTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.patch=patch.object(stats,'RACING',self.root);self.patch.start();self.addCleanup(self.patch.stop)
        self.clock=patch.object(stats.dt,'datetime',FixedDatetime);self.clock.start();self.addCleanup(self.clock.stop)
        self.prior=self.rows(2025,60,1000);self.current=self.rows(2026,40,1100)
        self.save(2025,self.prior);self.save(2026,self.current)
        (self.root/'handles_2025/comparison_2025_vs_2026.json').write_text(json.dumps({'year1_days':self.prior[:30],'year2_days':self.current[:30]}))
    def rows(self,year,count,value):
        return [{'date':(dt.date(year,4,18)+dt.timedelta(days=i)).isoformat(),'status':'ok','handle_cad':value,'races':8} for i in range(count)]
    def save(self,year,rows):
        folder=self.root/f'handles_{year}';folder.mkdir(exist_ok=True)
        (folder/'handles.json').write_text(json.dumps({'track':'WO','season':str(year),'daily':rows}))
    def test_thirty_day_export_cannot_truncate_full_ytd(self):
        result=stats.handles();self.assertEqual(result['current']['days'],40);self.assertEqual(result['previous']['days'],40)
        self.assertEqual(result['current']['handle'],44000);self.assertEqual(result['previous']['handle'],40000);self.assertAlmostEqual(result['change'],10)
        self.assertEqual(result['through'],self.current[-1]['date']);self.assertEqual(result['priorThrough'],self.prior[39]['date'])
        self.assertNotIn('handle-yoy',[d['key'] for d in result['documents']])
    def test_cancelled_days_do_not_count_but_unresolved_cards_fail_closed(self):
        self.save(2026,self.current+[{'date':'2026-06-01','status':'cancelled','handle_cad':None}]);self.assertEqual(stats.handles()['current']['days'],40)
        self.save(2026,self.current+[{'date':'2026-06-01','status':'ok','handle_cad':None}])
        with self.assertRaises(ValueError):stats.handles()
    def test_duplicate_dates_and_short_prior_season_cannot_produce_totals(self):
        self.save(2026,self.current+[self.current[0]])
        with self.assertRaises(ValueError):stats.handles()
        self.save(2026,self.current);self.save(2025,self.prior[:30])
        with self.assertRaises(ValueError):stats.handles()

if __name__=='__main__':unittest.main()
