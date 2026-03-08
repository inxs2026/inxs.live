"""
Vercel Python Serverless Function — /api/proxy
Proxies a video URL from Twitter's CDN so the browser downloads it
instead of opening it (bypasses CORS + Content-Disposition restriction).
"""

import json
import re
import urllib.request
import urllib.error
import urllib.parse
from http.server import BaseHTTPRequestHandler

MAX_URL_LEN = 2048
ALLOWED_HOSTS = re.compile(
    r'^https?://[^/]*\.twimg\.com/', re.IGNORECASE
)


def is_allowed_url(url: str) -> bool:
    """Only proxy requests to Twitter CDN domains."""
    if not url or len(url) > MAX_URL_LEN:
        return False
    return bool(ALLOWED_HOSTS.match(url))


class handler(BaseHTTPRequestHandler):

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        # Parse query string
        qs = ""
        if "?" in self.path:
            qs = self.path.split("?", 1)[1]

        params = {}
        for part in qs.split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                params[urllib.parse.unquote(k)] = urllib.parse.unquote_plus(v)

        video_url = params.get("url", "").strip()

        if not is_allowed_url(video_url):
            self._error(400, "Invalid or disallowed URL.")
            return

        filename = params.get("filename", "video.mp4")
        if not filename.endswith(".mp4"):
            filename += ".mp4"

        try:
            req = urllib.request.Request(
                video_url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/122.0.0.0 Safari/537.36"
                    ),
                    "Referer": "https://x.com/",
                    "Origin": "https://x.com",
                }
            )
            with urllib.request.urlopen(req, timeout=25) as resp:
                content_type = resp.headers.get("Content-Type", "video/mp4")
                data = resp.read()

        except urllib.error.HTTPError as e:
            self._error(502, f"Upstream error: {e.code}")
            return
        except Exception as e:
            self._error(502, f"Failed to fetch video: {str(e)}")
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", len(data))
        self.send_header("Cache-Control", "no-store")
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    def _error(self, status, message):
        body = json.dumps({"error": message}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass
