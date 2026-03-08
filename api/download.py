"""
Vercel Python Serverless Function — /api/download
Uses yt-dlp as a Python library (not subprocess) to extract the direct
CDN video URL from an X/Twitter post. Browser downloads straight from X.
"""

import json
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


def get_video_info(tweet_url: str) -> dict:
    try:
        import yt_dlp

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'http_headers': {
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/122.0.0.0 Safari/537.36'
                )
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(tweet_url, download=False)

        if not info:
            return {"error": "No video found in that post."}

        # Grab the best direct URL
        direct_url = None
        title = info.get('title', 'video')

        if info.get('url'):
            direct_url = info['url']
        elif info.get('formats'):
            # Pick best mp4 format
            mp4_formats = [
                f for f in info['formats']
                if f.get('ext') == 'mp4' and f.get('url')
            ]
            if mp4_formats:
                # Sort by resolution descending
                mp4_formats.sort(
                    key=lambda f: (f.get('height') or 0),
                    reverse=True
                )
                direct_url = mp4_formats[0]['url']
            else:
                # Fallback: last format with a URL
                for f in reversed(info['formats']):
                    if f.get('url'):
                        direct_url = f['url']
                        break

        if not direct_url:
            return {"error": "Could not extract a download URL from that post."}

        return {"url": direct_url, "title": title}

    except Exception as exc:
        msg = str(exc)
        if 'login' in msg.lower() or 'age' in msg.lower():
            return {"error": "That video requires a login to access."}
        if '429' in msg or 'rate limit' in msg.lower():
            return {"error": "X is rate-limiting requests — try again in a moment."}
        if 'No video' in msg or 'no formats' in msg.lower():
            return {"error": "No downloadable video found in that post."}
        return {"error": f"Could not extract video. Make sure the post contains a video."}


class handler(BaseHTTPRequestHandler):

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
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
            self._respond(400, {
                "error": "Only X (twitter.com or x.com) URLs are supported."
            })
            return

        result = get_video_info(url)
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
