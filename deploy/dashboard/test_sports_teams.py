import json,tempfile,unittest,os,time
from pathlib import Path
from unittest.mock import patch
import sports_teams as s
class TeamTests(unittest.TestCase):
    def test_dark_logo_and_valid_brand_colors(self):
        t={'displayName':'Buffalo Bills','color':'00338D','alternateColor':'C60C30','logos':[{'href':'https://a.espncdn.com/default.png','rel':['default']},{'href':'https://a.espncdn.com/dark.png','rel':['dark']}]}
        v=s.branding(t);self.assertEqual(v['logo'],'https://a.espncdn.com/dark.png');self.assertEqual(v['color'],'#00338d');self.assertEqual(v['alternateColor'],'#c60c30')
    def test_bad_assets_and_colors_are_rejected(self):
        for value in ['javascript:alert(1)','http://a.espncdn.com/logo.png','https://a.espncdn.com.evil/logo.png','https://user:pass@a.espncdn.com/logo.png']:self.assertIsNone(s.logo(value))
        self.assertIsNone(s.color('red;display:none'));self.assertIsNone(s.color(None))
    def test_competitor_preserves_scores_and_home_away(self):
        c={'team':{'id':'2','abbreviation':'BUF','displayName':'Buffalo Bills','logo':'https://a.espncdn.com/default.png'},'score':'31','homeAway':'away'}
        v=s.competitor(c,{'2':{'logo':'https://a.espncdn.com/dark.png','color':'#00338d','alternateColor':'#c60c30'}})
        self.assertEqual(v['score'],'31');self.assertFalse(v['home']);self.assertEqual(v['logo'],'https://a.espncdn.com/dark.png');self.assertEqual(v['color'],'#00338d')
    def test_metadata_failure_uses_cache_without_losing_scores(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(s,'CACHE',Path(folder)),patch.object(s.urllib.request,'urlopen',side_effect=OSError('offline')):
            p=Path(folder)/'football-nfl.json';p.write_text(json.dumps({'2':{'color':'#00338d'}}));os.utime(p,(time.time()-90000,)*2)
            self.assertEqual(s.registry('football/nfl')['2']['color'],'#00338d')
            self.assertEqual(s.registry('hockey/nhl'),{})
        with self.assertRaises(ValueError):s.registry('../private')
