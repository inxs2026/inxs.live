import unittest, tempfile
from pathlib import Path
from unittest.mock import patch
import race_schedule, racing
class ScheduleTests(unittest.TestCase):
    def test_offday_and_next_day(self):
        s=race_schedule.build('2026-10-05')
        self.assertIs(s['scheduled'],False)
        self.assertEqual(s['nextRaceDate'],'2026-10-08')
    def test_special_dates_and_season(self):
        for day,expected in [('2026-10-08',True),('2026-09-07',True),('2026-08-13',False),('2026-01-08',False)]:
            self.assertIs(race_schedule.build(day)['scheduled'],expected)
    def test_unknown_year_and_missing_calendar_do_not_hide_alerts(self):
        self.assertIsNone(race_schedule.build('2027-10-05')['scheduled'])
        with patch.object(race_schedule,'CALENDAR',Path('/nonexistent-calendar.json')):
            self.assertIsNone(race_schedule.build('2026-10-05')['scheduled'])
    def test_saved_card_overrides_stale_offday(self):
        self.assertIs(race_schedule.build('2026-10-05',True)['scheduled'],True)
    def test_no_offday_network_refresh_but_race_day_still_checks(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(racing,'HERMES',Path(folder)/'hermes'), patch.object(racing,'OPENCLAW',Path(folder)/'openclaw'), patch.object(racing,'enrichment',return_value=({},False)) as fetch:
            with patch.object(racing,'today',return_value='2026-10-05'):
                data=racing.build(offline=True)
                self.assertFalse(data['schedule']['scheduled']);self.assertEqual(data['races'],[]);fetch.assert_not_called()
            with patch.object(racing,'today',return_value='2026-10-08'):
                self.assertTrue(racing.build(offline=True)['schedule']['scheduled']);fetch.assert_called_once()
