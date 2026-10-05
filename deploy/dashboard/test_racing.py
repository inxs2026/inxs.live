import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import racing


class RacingTests(unittest.TestCase):
    def test_date_and_document_paths_reject_traversal(self):
        for value in ('../../etc/passwd', '2026-99-12', '2026-1-01', ''):
            with self.assertRaises(ValueError):
                racing.valid_date(value)
        with self.assertRaises(ValueError):
            racing.document_path('../hermes', '2026-10-04')

    def test_rankings_keep_missing_values_last_and_do_not_guess_program(self):
        data = {'horses': [{'name': 'No Figures', 'avg3': None, 'e_values': []}, {'name': 'Best (IRE)', 'avg3': 80, 'e_values': [85, 75]}, {'name': 'Other', 'avg3': 60, 'e_values': [60]}]}
        rows = racing.openclaw_rankings(data, {'best': '1A'})
        self.assertEqual([h['name'] for h in rows], ['Best (IRE)', 'Other', 'No Figures'])
        self.assertEqual(rows[0]['pp'], '1A')
        self.assertEqual(rows[1]['pp'], '')
        self.assertFalse(rows[1]['ppVerified'])

    def test_source_date_fallback_is_rejected(self):
        wrong = {'scratches': [{'race_date': '2026-10-03', 'track_code': 'WO'}]}
        with patch.object(racing, 'json_get', return_value=wrong), self.assertRaises(ValueError):
            racing.get_updates('scratches', '2026-10-04')
        with patch.object(racing, 'json_get', return_value={'scratches': [], 'meta': {'fallback_applied': True}}), self.assertRaises(ValueError):
            racing.get_updates('scratches', '2026-10-04')

    def test_scratch_feed_paginates(self):
        pages = [{'scratches': [{'race_date': '2026-10-04', 'track_code': 'WO', 'race_number': 1, 'horse_name': 'A'}], 'total_pages': 2}, {'scratches': [{'race_date': '2026-10-04', 'track_code': 'WO', 'race_number': 2, 'horse_name': 'B'}], 'total_pages': 2}]
        with patch.object(racing, 'json_get', side_effect=pages) as get:
            result = racing.get_updates('scratches', '2026-10-04')
        self.assertEqual(len(result['items']), 2)
        self.assertIn('page=2', get.call_args.args[0])

    def test_new_scratch_keeps_original_picks_and_official_pick_separate(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            hp = home / 'hermes/2026-10-04/artifacts'
            op = home / 'openclaw'
            hp.mkdir(parents=True)
            op.mkdir()
            (hp / 'picks-payload.json').write_text(json.dumps({'1': {'picks': [{'name': 'A', 'pp': 1, 'avg': 50, 'last3': [50]}, {'name': 'B', 'pp': 2, 'avg': 45, 'last3': [45]}], 'scratches': []}}))
            (hp.parent / 'state.json').write_text(json.dumps({'race_results': {'1': {'horses': {'1:a': {'name': 'A', 'pp': 1}, '2:b': {'name': 'B', 'pp': 2}}}}}))
            (op / 'WO--10-04-2026_smartpick.json').write_text(json.dumps({'track': 'WO', 'date': '2026-10-04', 'races': [{'race': 1, 'equibase_pick_pp': 2, 'horses': [{'name': 'A', 'avg3': 75, 'e_values': [75]}, {'name': 'B', 'avg3': 60, 'e_values': [60]}]}]}))
            live = {'scratches': {'items': [{'race': 1, 'pp': '1', 'name': 'A', 'reason': 'Vet'}], 'checkedAt': '2026-10-04T17:00:00Z'}}
            with patch.object(racing, 'HERMES', home / 'hermes'), patch.object(racing, 'OPENCLAW', op), patch.object(racing, 'today', return_value='2026-10-04'), patch.object(racing, 'enrichment', return_value=(live, False)):
                result = racing.build('2026-10-04')
            race = result['races'][0]
            self.assertEqual(race['hermes'][0]['name'], 'A')
            self.assertEqual(race['hermes'][0]['rank'], 1)
            self.assertTrue(race['hermes'][0]['scratched'])
            self.assertEqual(race['openclaw'][0]['name'], 'A')
            self.assertEqual(race['official']['name'], 'B')
            self.assertEqual(result['scratches']['source'], 'TrackData')


if __name__ == '__main__':
    unittest.main()
