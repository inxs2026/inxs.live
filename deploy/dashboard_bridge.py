#!/usr/bin/env python3
"""Authenticated dashboard bridge; scheduler access remains read-only for Vercel to the existing LAN Dashboard."""
import hmac
import json
import acknowledgements
import cameras
import os
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN = os.environ['DASHBOARD_ORIGIN_TOKEN']
if len(TOKEN) < 32:
    raise RuntimeError('Origin token must contain at least 32 characters')
PATHS = {'/api/jobs', '/api/codex-usage', '/api/sports-scores', '/api/sports-standings', '/api/system-health', '/api/timeline', '/api/racing-performance',
         '/api/racing', '/api/woodbine-stats', '/api/stocks', '/api/stock-quotes',
         '/api/briefing', '/api/health', '/agco-document', '/racing-document',
         '/stats-document', '/stock-document'}
SLOTS = threading.BoundedSemaphore(8)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if not hmac.compare_digest(self.headers.get('Authorization', ''), 'Bearer ' + TOKEN):
            return self.respond(401, b'{"error":"Unauthorized"}', 'application/json')
        if urllib.parse.urlsplit(self.path).path != '/api/acknowledgements':
            return self.respond(405, b'{"error":"Method not allowed"}', 'application/json')
        try:
            length=int(self.headers.get('Content-Length', '0'))
            if length < 1 or length > 65536:
                raise ValueError('Invalid body')
            form=urllib.parse.parse_qs(self.rfile.read(length).decode(),strict_parsing=True)
            result=acknowledgements.observe(json.loads(form['notices'][0]),form.get('complete',['false'])[0]=='true') if 'notices' in form else acknowledgements.acknowledge(form.get('key',[''])[0])
            self.respond(200,json.dumps(result).encode(),'application/json')
        except (ValueError,UnicodeError):
            self.respond(400,b'{"error":"Invalid acknowledgement"}','application/json')
        except Exception:
            self.respond(503,b'{"error":"Acknowledgement could not be saved"}','application/json')

    def do_GET(self):
        if not hmac.compare_digest(self.headers.get('Authorization', ''), 'Bearer ' + TOKEN):
            return self.respond(401, b'{"error":"Unauthorized"}', 'application/json')
        url = urllib.parse.urlsplit(self.path)
        if url.path == '/api/cameras':
            try:
                requested = urllib.parse.parse_qs(url.query).get('channels', [''])[0]
                channels = {int(x) for x in requested.split(',') if x}
                if not channels <= set(range(1,7)): raise ValueError('Invalid channel')
                return self.respond(200,json.dumps(cameras.relay.status(channels)).encode(),'application/json')
            except ValueError:
                return self.respond(400,b'{"error":"Invalid camera selection"}','application/json')
            except Exception:
                return self.respond(503,b'{"error":"Camera connection unavailable"}','application/json')
        if url.path.startswith('/camera-stream/'):
            status,body,content_type = cameras.relay.read(url.path)
            return self.respond(status,body,content_type)
        if url.path == '/api/acknowledgements':
            try:
                return self.respond(200,json.dumps(acknowledgements.listing()).encode(),'application/json')
            except Exception:
                return self.respond(503,b'{"error":"Acknowledgements unavailable"}','application/json')
        if url.path not in PATHS:
            return self.respond(404, b'{"error":"Not found"}', 'application/json')
        if not SLOTS.acquire(blocking=False):
            return self.respond(503, b'{"error":"Please retry"}', 'application/json')
        try:
            target = 'http://10.0.0.49:8088' + url.path + ('?' + url.query if url.query else '')
            with urllib.request.urlopen(target, timeout=23) as response:
                self.respond(response.status, response.read(), response.headers.get('Content-Type', 'application/json'))
        except urllib.error.HTTPError as exc:
            self.respond(exc.code, b'{"error":"Report unavailable or invalid request"}', 'application/json')
        except Exception:
            self.respond(502, b'{"error":"Linux dashboard unavailable"}', 'application/json')
        finally:
            SLOTS.release()

    def respond(self, status, body, content_type):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'private, no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Do not log credentials, queries, or report names.
        pass


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 8089), Handler)
    server.daemon_threads = True
    server.serve_forever()
