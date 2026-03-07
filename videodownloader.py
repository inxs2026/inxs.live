#!/usr/bin/env python3
"""
X Video Downloader
A simple Flask web app to download videos from X (Twitter).
Usage: python3 app.py
"""

from flask import Flask, request, send_file, render_template_string
import subprocess
import os

app = Flask(__name__)

# Configuration
DOWNLOADS_DIR = os.path.expanduser("~/downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Simple HTML template
HTML = """
<!doctype html>
<html>
<head>
    <title>X Video Downloader</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               max-width: 600px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
        h1 { text-align: center; color: #333; }
        form { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; 
                box-sizing: border-box; font-size: 16px; }
        button { width: 100%; background: #1da1f2; color: white; padding: 12px; border: none; 
                 border-radius: 4px; font-size: 16px; cursor: pointer; }
        button:hover { background: #0d8bd9; }
        .result { margin-top: 20px; text-align: center; }
        .result a { color: #1da1f2; text-decoration: none; font-size: 18px; }
        .error { color: red; text-align: center; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>🐦 X Video Downloader</h1>
    <form method="post">
        <input type="url" name="url" placeholder="Paste X (Twitter) video URL..." required>
        <button type="submit">Download</button>
    </form>
    {% if error %}
    <p class="error">{{ error }}</p>
    {% endif %}
    {% if filename %}
    <div class="result">
        <p>✅ Download complete!</p>
        <a href="/download/{{ filename }}">⬇️ Download: {{ filename }}</a>
    </div>
    {% endif %}
</body>
</html>
"""


@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    filename = None

    if request.method == 'POST':
        url = request.form.get('url', '').strip()

        if not url:
            error = "Please enter a URL"
        else:
            try:
                # Download video using yt-dlp
                output_path = os.path.join(DOWNLOADS_DIR, "%(title)s.%(ext)s")
                result = subprocess.run(
                    ['yt-dlp', '-o', output_path, '--no-playlist', url],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode != 0:
                    error = f"Download failed: {result.stderr}"
                else:
                    # Get most recent file
                    files = [f for f in os.listdir(DOWNLOADS_DIR) 
                            if os.path.isfile(os.path.join(DOWNLOADS_DIR, f))]
                    if files:
                        files.sort(key=lambda f: os.path.getmtime(os.path.join(DOWNLOADS_DIR, f)), 
                                  reverse=True)
                        filename = files[0]
                    else:
                        error = "Download seemed to succeed but no file found"

            except subprocess.TimeoutExpired:
                error = "Download timed out (too large?)"
            except Exception as e:
                error = f"Error: {str(e)}"

    return render_template_string(HTML, error=error, filename=filename)


@app.route('/download/<filename>')
def download_file(filename):
    """Serve the downloaded file."""
    return send_file(
        os.path.join(DOWNLOADS_DIR, filename),
        as_attachment=True
    )


if __name__ == '__main__':
    print(f"🚀 X Video Downloader running at http://localhost:5050")
    app.run(host='0.0.0.0', port=5050, debug=False)
