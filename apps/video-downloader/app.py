import os
import re
import shutil
import subprocess
import threading
import time
import uuid
from pathlib import Path

JOB_TTL_SECONDS = 3600  # remove completed/errored jobs after 1 hour

from flask import Flask, abort, jsonify, render_template, request, send_file

try:
    import yt_dlp
except ImportError:
    yt_dlp = None


BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = Path(os.environ.get("DOWNLOAD_DIR", str(Path.home() / "Downloads"))).expanduser()
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
OPEN_DOWNLOADS_ENABLED = os.environ.get("ENABLE_OPEN_DOWNLOADS", "").lower() in {"1", "true", "yes"}
COOKIES_FILE = os.environ.get("COOKIES_FILE", "").strip() or None

app = Flask(__name__)

jobs = {}
jobs_lock = threading.Lock()


URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)


def _safe_percent(value: str) -> float:
    if not value:
        return 0.0
    cleaned = value.replace("%", "").strip()
    try:
        return max(0.0, min(100.0, float(cleaned)))
    except ValueError:
        return 0.0


def _set_job(job_id: str, **updates):
    with jobs_lock:
        job = jobs.get(job_id, {})
        job.update(updates)
        jobs[job_id] = job
        # Evict old completed/errored jobs to prevent unbounded memory growth.
        now = int(time.time())
        stale = [
            jid for jid, j in jobs.items()
            if j.get("status") in ("completed", "error")
            and now - int(j.get("completed_at") or j.get("created_at") or now) > JOB_TTL_SECONDS
        ]
        for jid in stale:
            jobs.pop(jid, None)


class _CapturingLogger:
    def __init__(self):
        self.lines = []

    def debug(self, msg):
        self.lines.append(msg)

    def info(self, msg):
        self.lines.append(msg)

    def warning(self, msg):
        self.lines.append(f"WARNING: {msg}")

    def error(self, msg):
        self.lines.append(f"ERROR: {msg}")


def _download_worker(job_id: str, url: str, format_choice: str):
    if yt_dlp is None:
        _set_job(job_id, status="error", error="Missing dependency: yt-dlp is not installed.")
        return

    # Keep names very short for fragment/temp suffixes used by some extractors.
    output_template = str(DOWNLOAD_DIR / "%(id)s_%(title).30s.%(ext)s")

    logger = _CapturingLogger()

    def progress_hook(data):
        status = data.get("status")
        if status == "downloading":
            percent = _safe_percent(data.get("_percent_str", "0"))
            speed = (data.get("_speed_str") or "").strip()
            eta = str(data.get("eta") or "").strip()
            _set_job(
                job_id,
                status="downloading",
                progress=percent,
                speed=speed,
                eta=eta,
                message="Downloading...",
            )
        elif status == "finished":
            _set_job(job_id, status="processing", progress=97.0, message="Processing file...")

    ydl_opts = {
        "outtmpl": output_template,
        "progress_hooks": [progress_hook],
        "noplaylist": True,
        "quiet": True,
        "no_warnings": False,
        "verbose": True,
        "logger": logger,
        "restrictfilenames": False,
    }

    if COOKIES_FILE and Path(COOKIES_FILE).is_file():
        ydl_opts["cookiefile"] = COOKIES_FILE

    if format_choice == "mp3":
        if shutil.which("ffmpeg") is None:
            _set_job(
                job_id,
                status="error",
                error="MP3 conversion requires ffmpeg. Install ffmpeg and try again.",
                message="Download failed",
            )
            return
        ydl_opts.update(
            {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
        )
    elif format_choice == "mp4":
        ydl_opts.update(
            {
                # Prefer MP4 files that already include audio, then fallback to any format with audio.
                "format": "best[ext=mp4][acodec!=none]/best[acodec!=none]/best",
            }
        )
    else:
        ydl_opts.update({"format": "bestvideo*+bestaudio/best"})

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            # yt-dlp may change extension after post-processing.
            base = os.path.splitext(filename)[0]
            if format_choice == "mp3":
                mp3_file = Path(base + ".mp3")
                if mp3_file.exists():
                    filename = str(mp3_file)
                else:
                    matches = list(Path(base).parent.glob(Path(base).name + ".*"))
                    mp3_matches = [p for p in matches if p.suffix.lower() == ".mp3"]
                    if mp3_matches:
                        filename = str(mp3_matches[0])
                    elif matches:
                        filename = str(matches[0])
            elif not os.path.exists(filename):
                matches = list(Path(base).parent.glob(Path(base).name + ".*"))
                if matches:
                    filename = str(matches[0])

            _set_job(
                job_id,
                status="completed",
                progress=100.0,
                speed="",
                eta="",
                message="Download complete",
                file_path=filename,
                title=info.get("title", "Untitled"),
                extractor=info.get("extractor_key", "Unknown"),
                selected_format=format_choice,
                completed_at=int(time.time()),
            )
    except Exception as exc:
        _set_job(job_id, status="error", error=str(exc), message="Download failed",
                 debug_log="\n".join(logger.lines[-80:]))


@app.get("/")
def index():
    return render_template(
        "index.html",
        downloads_path=str(DOWNLOAD_DIR),
        downloads_uri=DOWNLOAD_DIR.as_uri(),
        open_downloads_enabled=OPEN_DOWNLOADS_ENABLED,
    )


@app.get("/healthz")
def healthcheck():
    return jsonify({"status": "ok"})


@app.get("/api/debug")
def debug_env():
    def run(cmd):
        try:
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=5).decode().strip()
        except Exception as e:
            return f"ERROR: {e}"

    # Check bgutil plugin by trying to import it directly
    bgutil_plugin_status = {}
    for mod in [
        "yt_dlp_plugins",
        "yt_dlp_plugins.extractor",
        "yt_dlp_plugins.extractor.getpot_bgutil",
    ]:
        try:
            __import__(mod)
            bgutil_plugin_status[mod] = "OK"
        except ImportError as e:
            bgutil_plugin_status[mod] = f"ImportError: {e}"

    # Check bgutil HTTP reachability
    try:
        import urllib.request
        urllib.request.urlopen("http://127.0.0.1:4416", timeout=2)
        bgutil_http = "reachable"
    except Exception as e:
        bgutil_http = f"ERROR: {e}"

    # Check curl_cffi
    try:
        import curl_cffi
        curl_cffi_version = curl_cffi.__version__
    except ImportError:
        curl_cffi_version = "NOT INSTALLED"

    # List yt-dlp plugin dirs
    try:
        import yt_dlp.plugins
        plugin_dirs = [str(d) for d in getattr(yt_dlp.plugins, "PACKAGE_NAME", [])]
    except Exception:
        plugin_dirs = []

    return jsonify({
        "yt_dlp_version": yt_dlp.version.__version__ if yt_dlp else "NOT INSTALLED",
        "deno": run(["deno", "--version"]).splitlines()[0] if shutil.which("deno") else "NOT FOUND",
        "bgutil_pot": run(["bgutil-pot", "--version"]) if shutil.which("bgutil-pot") else "NOT FOUND",
        "bgutil_running": run(["pgrep", "-a", "bgutil-pot"]),
        "bgutil_http": bgutil_http,
        "bgutil_plugin": bgutil_plugin_status,
        "ffmpeg": run(["ffmpeg", "-version"]).splitlines()[0] if shutil.which("ffmpeg") else "NOT FOUND",
        "curl_cffi": curl_cffi_version,
        "yt_dlp_plugin_dirs": plugin_dirs,
        "cookies_file": COOKIES_FILE or "not set",
        "download_dir": str(DOWNLOAD_DIR),
    })


@app.get("/api/last-error")
def last_error():
    with jobs_lock:
        failed = [j for j in jobs.values() if j.get("status") == "error"]
    if not failed:
        return jsonify({"message": "No failed jobs found"}), 404
    latest = max(failed, key=lambda j: j.get("created_at", 0))
    return jsonify(latest)


@app.post("/api/download")
def start_download():
    payload = request.get_json(silent=True) or {}
    url = (payload.get("url") or "").strip()
    format_choice = (payload.get("format") or "best_quality").strip()

    if not url or not URL_PATTERN.match(url):
        return jsonify({"error": "Please enter a valid URL (http/https)."}), 400
    if format_choice not in {"best_quality", "mp4", "mp3"}:
        return jsonify({"error": "Invalid format option."}), 400

    job_id = str(uuid.uuid4())
    _set_job(
        job_id,
        status="queued",
        progress=0.0,
        speed="",
        eta="",
        message="Queued",
        selected_format=format_choice,
        created_at=int(time.time()),
    )

    thread = threading.Thread(target=_download_worker, args=(job_id, url, format_choice), daemon=True)
    thread.start()

    return jsonify({"job_id": job_id})


@app.get("/api/status/<job_id>")
def get_status(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)

    if not job:
        return jsonify({"error": "Job not found"}), 404

    return jsonify(job)


@app.get("/api/file/<job_id>")
def get_file(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)

    if not job or job.get("status") != "completed":
        return abort(404)

    file_path = Path(job.get("file_path", "")).resolve()
    downloads_root = DOWNLOAD_DIR.resolve()

    if not str(file_path).startswith(str(downloads_root)) or not file_path.exists():
        return abort(404)

    return send_file(file_path, as_attachment=True)


@app.post("/api/open-downloads")
def open_downloads():
    if not OPEN_DOWNLOADS_ENABLED:
        return jsonify({"error": "Opening the downloads folder is disabled on this server."}), 403

    opener = shutil.which("xdg-open")
    if opener is None:
        return jsonify({"error": "xdg-open is not available on this system."}), 500

    try:
        subprocess.Popen([opener, str(DOWNLOAD_DIR)])
    except Exception as exc:
        return jsonify({"error": f"Unable to open folder: {exc}"}), 500

    return jsonify({"ok": True, "path": str(DOWNLOAD_DIR)})


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "4000"))
    app.run(host=host, port=port, debug=False)
