"""On-demand authenticated Lorex video relay. No recorder credentials leave Linux."""
import json
import re
import subprocess
import threading
import time
import urllib.parse
from pathlib import Path

CONFIG = Path.home() / '.config/inxs-dashboard/cameras.json'
ROOT = Path.home() / '.local/state/inxs-dashboard/cameras'
VALID = re.compile(r'^/camera-stream/([1-6])/(index\.m3u8|segment_[0-9]+\.ts)$')
IDLE_SECONDS = 90

class Relay:
    def __init__(self):
        self.lock = threading.RLock()
        self.workers = {}
        self.access = {}
        self.retry = {}
        self.auth_blocked = {}
        threading.Thread(target=self.reap, daemon=True).start()

    def config(self):
        try:
            c = json.loads(CONFIG.read_text())
            if c.get('host') != '10.0.0.105' or not c.get('username') or not c.get('password'):
                return None
            return c
        except (OSError, ValueError):
            return None

    def stop(self, channel):
        proc = self.workers.pop(channel, None)
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try: proc.wait(timeout=1)
            except subprocess.TimeoutExpired: proc.kill(); proc.wait(timeout=1)

    def start(self, channel, config):
        now = time.monotonic()
        self.access[channel] = now
        version = CONFIG.stat().st_mtime_ns
        if self.auth_blocked.get(channel) == version: return
        folder = ROOT / str(channel)
        playlist = folder / 'index.m3u8'
        proc = self.workers.get(channel)
        if proc is not None and proc.poll() is None:
            if playlist.exists() and time.time() - playlist.stat().st_mtime > 30:
                self.stop(channel)
            else: return
        if now < self.retry.get(channel, 0): return
        self.stop(channel)
        self.retry[channel] = now + 20
        folder.mkdir(parents=True, exist_ok=True, mode=0o700)
        for file in folder.iterdir():
            if re.fullmatch(r'(index\.m3u8|segment_[0-9]+\.ts)(\.tmp)?', file.name):
                file.unlink(missing_ok=True)
        user = urllib.parse.quote(config['username'], safe='')
        password = urllib.parse.quote(config['password'], safe='')
        recorder_channel = int(config.get('channels', [1,2,3,4,5,6])[channel-1])
        stream = f'rtsp://{user}:{password}@10.0.0.105:554/cam/realmonitor?channel={recorder_channel}&subtype=1'
        command = ['ffmpeg','-nostdin','-hide_banner','-loglevel','error',
            '-rtsp_transport','tcp','-timeout','10000000','-i',stream,
            '-map','0:v:0','-an','-vf','scale=640:-2,fps=10',
            '-c:v','libx264','-preset','ultrafast','-tune','zerolatency',
            '-threads','1','-pix_fmt','yuv420p','-b:v','350k','-maxrate','500k','-bufsize','700k',
            '-g','20','-sc_threshold','0','-f','hls','-hls_time','2','-hls_list_size','6',
            '-hls_delete_threshold','3','-hls_flags','delete_segments+temp_file+program_date_time',
            '-hls_start_number_source','epoch','-hls_segment_filename',str(folder/'segment_%d.ts'),str(playlist)]
        try:
            self.workers[channel] = subprocess.Popen(command, stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            threading.Thread(target=self.watch_errors,args=(channel,self.workers[channel],version),daemon=True).start()
        except OSError:
            self.retry[channel] = now + 30

    def watch_errors(self, channel, proc, version):
        # Classify authentication failures without retaining URLs or credentials.
        denied = False
        for line in proc.stderr:
            if b'401 Unauthorized' in line or b'authorization failed' in line: denied = True
        proc.stderr.close()
        if denied:
            with self.lock:
                if self.workers.get(channel) is proc: self.auth_blocked[channel] = version

    def status(self, channels):
        config = self.config()
        with self.lock:
            if config:
                for channel in channels: self.start(channel, config)
            result = []
            for channel in range(1,7):
                playlist = ROOT / str(channel) / 'index.m3u8'
                proc = self.workers.get(channel)
                running = proc is not None and proc.poll() is None
                fresh = playlist.exists() and time.time()-playlist.stat().st_mtime < 20
                state = 'signin-required' if config and self.auth_blocked.get(channel) == CONFIG.stat().st_mtime_ns else 'ready' if running and fresh else 'starting' if running else 'idle' if channel not in channels else 'unavailable'
                result.append({'id':channel,'name':f'Camera {channel}','state':state if config else 'setup-required',
                    'stream':f'/camera-stream/{channel}/index.m3u8'})
            return {'cameras':result,'configured':bool(config),'note':('Recorder login or remote live-view permission needs checking.' if any(c['state']=='signin-required' for c in result) else 'Live video has a short delay.') if config else 'Recorder login is needed to connect the cameras.'}

    def read(self, path):
        match = VALID.fullmatch(path)
        if not match: return 404, b'Not found', 'text/plain'
        channel = int(match[1])
        with self.lock:
            self.access[channel] = time.monotonic()
            proc = self.workers.get(channel)
            playlist = ROOT / str(channel) / 'index.m3u8'
            if proc is None or proc.poll() is not None or not playlist.exists() or time.time()-playlist.stat().st_mtime > 30:
                return 503, b'Camera stream unavailable', 'text/plain'
            file = ROOT / str(channel) / match[2]
            try:
                if file.is_symlink() or file.stat().st_size > 3_500_000: return 404, b'Not found', 'text/plain'
                body = file.read_bytes()
            except OSError: return 404, b'Not found', 'text/plain'
            return 200, body, 'application/vnd.apple.mpegurl' if file.suffix == '.m3u8' else 'video/mp2t'

    def reap(self):
        while True:
            time.sleep(10)
            with self.lock:
                for channel in list(self.workers):
                    if time.monotonic()-self.access.get(channel,0)>IDLE_SECONDS: self.stop(channel)

relay = Relay()
