import io,json,os,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
import cameras

class FakeProcess:
    def __init__(self): self.stderr=io.BytesIO(b'');self.code=None
    def poll(self): return self.code
    def terminate(self): self.code=0
    def wait(self,timeout=None): return self.code
    def kill(self): self.code=-9

class CameraTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.config=self.root/'private.json'
        self.config.write_text(json.dumps({'host':'10.0.0.105','username':'fixture','password':'private fixture','channels':[1,2,3,4,5,6]}))
        self.patches=[patch.object(cameras,'CONFIG',self.config),patch.object(cameras,'ROOT',self.root/'streams')]
        for p in self.patches:p.start()
        self.relay=cameras.Relay()
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.temp.cleanup()
    def test_missing_config_reports_setup_without_starting(self):
        self.config.unlink()
        with patch.object(cameras.subprocess,'Popen') as launch:
            result=self.relay.status({1,2,3,4,5,6});launch.assert_not_called()
        self.assertFalse(result['configured']);self.assertTrue(all(c['state']=='setup-required' for c in result['cameras']))
    def test_only_selected_channels_start_and_public_data_has_no_credentials(self):
        with patch.object(cameras.subprocess,'Popen',side_effect=lambda *a,**k:FakeProcess()) as launch:
            result=self.relay.status({2});self.assertEqual(launch.call_count,1)
            self.assertIn('channel=2&subtype=1',launch.call_args.args[0][launch.call_args.args[0].index('-i')+1])
            self.relay.status({2});self.assertEqual(launch.call_count,1)
        self.assertNotIn('private fixture',json.dumps(result));self.assertNotIn('rtsp:',json.dumps(result))
    def test_auth_failure_waits_for_corrected_credentials(self):
        proc=FakeProcess();proc.stderr=io.BytesIO(b'401 Unauthorized\n');self.relay.workers[1]=proc
        self.relay.watch_errors(1,proc,self.config.stat().st_mtime_ns)
        with patch.object(cameras.subprocess,'Popen') as launch:
            self.assertEqual(self.relay.status({1})['cameras'][0]['state'],'signin-required');launch.assert_not_called()
    def test_streams_reject_invalid_paths_symlinks_and_stale_video(self):
        for path in ['/camera-stream/7/index.m3u8','/camera-stream/1/../../private.json','/camera-stream/1/private.json']:
            self.assertEqual(self.relay.read(path)[0],404)
        folder=cameras.ROOT/'1';folder.mkdir(parents=True);playlist=folder/'index.m3u8';playlist.write_text('#EXTM3U\nsegment_1.ts\n')
        self.relay.workers[1]=FakeProcess()
        self.assertEqual(self.relay.read('/camera-stream/1/index.m3u8')[0],200)
        (folder/'segment_1.ts').symlink_to(self.config)
        self.assertEqual(self.relay.read('/camera-stream/1/segment_1.ts')[0],404)
        os.utime(playlist,(time.time()-60,)*2)
        self.assertEqual(self.relay.read('/camera-stream/1/index.m3u8')[0],503)

if __name__=='__main__':unittest.main()
