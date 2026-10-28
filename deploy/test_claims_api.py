import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import claims_api


class ClaimsApiTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'reports').mkdir()
        self.year = datetime.now(ZoneInfo('America/Toronto')).year
        self.path = self.root / 'reports' / f'woodbine-claims-{self.year}-year-to-date.json'
        self.data = dict(year=self.year, track='Woodbine', complete=True, missing_dates=[], errors=[],
            claims=[dict(claim_price_cad='25000.00')], total_claims=1, total_claim_value_cad='25000.00',
            coverage_through=f'{self.year}-10-25', daily=dict(date=f'{self.year}-10-25'),
            checked_at=datetime.now(timezone.utc).isoformat())
        self.path.write_text(json.dumps(self.data))
        self.override = patch.object(claims_api, 'ROOT', self.root)
        self.override.start()

    def tearDown(self):
        self.override.stop()
        self.temp.cleanup()

    def test_complete_balanced_report_is_served(self):
        result = claims_api.read_report()
        self.assertEqual(result['total_claims'], 1)
        self.assertFalse(result['refresh']['stale'])

    def test_incomplete_or_unbalanced_snapshot_is_rejected(self):
        for change in [dict(complete=False), dict(total_claims=3), dict(total_claim_value_cad='0.00'), dict(year=2000)]:
            self.path.write_text(json.dumps(dict(self.data, **change)))
            with self.assertRaises(ValueError):
                claims_api.read_report()

    def test_failed_refresh_retains_data_and_marks_it_stale(self):
        (self.root / 'refresh-status.json').write_text(json.dumps(dict(error=True)))
        result = claims_api.read_report()
        self.assertEqual(result['claims'], self.data['claims'])
        self.assertTrue(result['refresh']['stale'])
        self.assertIn('last complete report', result['refresh']['error'])

    def test_missing_data_is_not_a_zero_claim_report(self):
        self.path.unlink()
        with self.assertRaises(OSError):
            claims_api.read_report()


if __name__ == '__main__':
    unittest.main()
