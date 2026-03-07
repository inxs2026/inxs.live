"""
Vercel Python Serverless Function — /api/download
Extracts the direct video URL from an X (Twitter) post using yt-dlp.
Returns JSON with the direct CDN URL so the browser downloads
straight from X — no file storage, no size limits on our end.
"""

import json
import subprocess
import re
from http.server import BaseHTTPRequestHandler

ALLOWED_DOMAINS = re.compile(
    r'^https?://(www\.)?(twitter\.com|x\.com|t\.co)/', re.IGNORECASE
)
MAX_URL_LEN = 512


def is_valid_url(url: str) -> bool:
    if not url or len(url) > MAX_URL_LEN:
        return False
    return bool(ALLOWED_DOMAINS.match(url))


def get_video_url(tweet_url: str) -> dict:
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--no-playlist", "--no-warnings",
                "-g",
                "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "--user-agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36",
                tweet_url,
            ],
            capture_output=True, text=True, timeout=30,
        )

        if result.returncode != 0:
            stderr = result.stderr.strip()
            if "No video" in stderr or "no formats" in stderr.lower():
                return {"error": "No downloadable video found in that post."}
            if "429" in stderr or "rate limit" in stderr.lower():
                return {"error": "X is rate-limiting us — try again in a moment."}
            if "login" in stderr.lower() or "age" in stderr.lower():
                return {"error": "That video requires a login to access."}
            return {"error": "Could not extract video. Make sure the post contains a video."}

        lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
        if not lines:
            return {"error": "No video URL found — the post may not contain a video."}

        return {"url": lines[0]}

    except subprocess.TimeoutExpired:
        return {"error": "Request timed out. The video may be too large or X is slow."}
    except FileNotFoundError:
        return {"error": "yt-dlp is not available on this server."}
    except Exception as exc:
        return {"error": f"Unexpected error: {exc}"}


class handler(BaseHTTPRequestHandler):
    """Vercel Python runtime expects a class named 'handler'."""

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "https://inxs.live")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
        except Exception:
            self._respond(400, {"error": "Invalid request body."})
            return

        url = (body.get("url") or "").strip()
        if not is_valid_url(url):
            self._respond(400, {"error": "Only X (twitter.com / x.com) URLs are supported."})
            return

        result = get_video_url(url)
        self._respond(200 if "url" in result else 422, result)

    def _respond(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass
