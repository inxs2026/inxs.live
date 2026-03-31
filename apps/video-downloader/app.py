import json
import os
import re
import shutil
import subprocess
import threading
import time
import uuid
from pathlib import Path

JOB_TTL_SECONDS = 3600  # remove completed/errored jobs after 1 hour

from flask import Flask, abort, jsonify, render_template, request, send_file, send_from_directory

try:
    import yt_dlp
except ImportError:
    yt_dlp = None


BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = Path(os.environ.get("DOWNLOAD_DIR", str(Path.home() / "Downloads"))).expanduser()
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
JOB_STATE_DIR = Path(
    os.environ.get("JOB_STATE_DIR", str(DOWNLOAD_DIR / ".video-downloader-jobs"))
).expanduser()
JOB_STATE_DIR.mkdir(parents=True, exist_ok=True)
OPEN_DOWNLOADS_ENABLED = os.environ.get("ENABLE_OPEN_DOWNLOADS", "").lower() in {"1", "true", "yes"}
COOKIES_FILE = os.environ.get("COOKIES_FILE", "").strip() or None

app = Flask(__name__)

jobs = {}
jobs_lock = threading.Lock()


URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(app.static_folder, "favicon.ico", mimetype="image/vnd.microsoft.icon")


def is_youtube_url(url: str) -> bool:
    lowered = url.lower()
    return "youtube.com/" in lowered or "youtu.be/" in lowered


def _safe_percent(value: str) -> float:
    if not value:
        return 0.0
    cleaned = value.replace("%", "").strip()
    try:
        return max(0.0, min(100.0, float(cleaned)))
    except ValueError:
        return 0.0


def _job_file(job_id: str) -> Path:
    return JOB_STATE_DIR / f"{job_id}.json"


def _load_job_from_disk(job_id: str):
    path = _job_file(job_id)
    if not path.exists():
        return None

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    return payload if isinstance(payload, dict) else None


def _persist_job(job_id: str, job: dict):
    path = _job_file(job_id)
    temp_path = path.with_suffix(".json.tmp")
    temp_path.write_text(json.dumps(job), encoding="utf-8")
    temp_path.replace(path)


def _cleanup_stale_jobs(now: int):
    stale_memory_ids = [
        jid for jid, job in jobs.items()
        if job.get("status") in ("completed", "error")
        and now - int(job.get("completed_at") or job.get("created_at") or now) > JOB_TTL_SECONDS
    ]

    for jid in stale_memory_ids:
        jobs.pop(jid, None)

    for path in JOB_STATE_DIR.glob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        completed_or_created = int(payload.get("completed_at") or payload.get("created_at") or now)
        if payload.get("status") in ("completed", "error") and now - completed_or_created > JOB_TTL_SECONDS:
            try:
                path.unlink()
            except OSError:
                pass


def _set_job(job_id: str, **updates):
    disk_job = _load_job_from_disk(job_id) or {}

    with jobs_lock:
        job = dict(disk_job)
        job.update(jobs.get(job_id, {}))
        job.update(updates)
        job.setdefault("job_id", job_id)
        job.setdefault("created_at", int(time.time()))
        jobs[job_id] = job
        now = int(time.time())
        _persist_job(job_id, job)
        _cleanup_stale_jobs(now)


def _get_job(job_id: str):
    with jobs_lock:
        in_memory = jobs.get(job_id)
        if in_memory:
            return dict(in_memory)

    job = _load_job_from_disk(job_id)
    if not job:
        return None

    with jobs_lock:
        jobs[job_id] = job

    return dict(job)


def _list_jobs():
    combined = {}

    with jobs_lock:
        for job_id, job in jobs.items():
            combined[job_id] = dict(job)

    for path in JOB_STATE_DIR.glob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        job_id = payload.get("job_id") or path.stem
        existing = combined.get(job_id, {})
        merged = dict(payload)
        merged.update(existing)
        merged.setdefault("job_id", job_id)
        combined[job_id] = merged

    return list(combined.values())


def _resolve_output_file(filename: str, format_choice: str, info: dict):
    if os.path.exists(filename):
        return filename

    base = os.path.splitext(filename)[0]
    matches = list(Path(base).parent.glob(Path(base).name + ".*"))

    if format_choice == "mp3":
        mp3_matches = [p for p in matches if p.suffix.lower() == ".mp3"]
        if mp3_matches:
            return str(mp3_matches[0])

    if matches:
        return str(matches[0])

    video_id = info.get("id")
    if video_id:
        fallback_matches = sorted(
            DOWNLOAD_DIR.glob(f"{video_id}_*"),
            key=lambda path: path.stat().st_mtime if path.exists() else 0,
            reverse=True,
        )
        if format_choice == "mp3":
            mp3_matches = [path for path in fallback_matches if path.suffix.lower() == ".mp3"]
            if mp3_matches:
                return str(mp3_matches[0])
        if fallback_matches:
            return str(fallback_matches[0])

    return filename


def _resolve_job_file(job: dict):
    file_path_value = job.get("file_path")
    downloads_root = DOWNLOAD_DIR.resolve()

    if file_path_value:
        file_path = Path(file_path_value).resolve()
        if str(file_path).startswith(str(downloads_root)) and file_path.exists():
            return file_path

    video_id = job.get("video_id")
    if video_id:
        matches = sorted(
            DOWNLOAD_DIR.glob(f"{video_id}_*"),
            key=lambda path: path.stat().st_mtime if path.exists() else 0,
            reverse=True,
        )
        if matches:
            return matches[0].resolve()

    return None


def _run_download_attempt(job_id: str, url: str, ydl_opts: dict):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        _set_job(
            job_id,
            status="initializing",
            progress=0.0,
            speed="",
            eta="",
            message="Fetching metadata...",
        )
        info = ydl.extract_info(url, download=False)
        _set_job(
            job_id,
            status="starting",
            progress=0.0,
            title=info.get("title", "Untitled"),
            video_id=info.get("id"),
            extractor=info.get("extractor_key", "Unknown"),
            message="Starting download...",
        )
        ydl.process_ie_result(info, download=True)
        filename = ydl.prepare_filename(info)
        return info, filename


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
            eta = (data.get("_eta_str") or str(data.get("eta") or "")).strip()
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
        "continuedl": True,
        "fragment_retries": 10,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": False,
        "verbose": True,
        "logger": logger,
        "retries": 10,
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
                "format": "bestvideo[vcodec^=avc1]+bestaudio[acodec^=mp4a]/best[ext=mp4]/best",
                "merge_output_format": "mp4",
            }
        )
    else:
        ydl_opts.update({"format": "bestvideo+bestaudio/best"})

    try:
        attempt_opts = [ydl_opts]

        if is_youtube_url(url):
            fallback_opts = dict(ydl_opts)
            fallback_opts["extractor_args"] = {
                "youtube": {
                    "player_client": ["web"],
                    "formats": ["incomplete"],
                }
            }
            attempt_opts.append(fallback_opts)

        info = None
        filename = None
        last_error = None

        for attempt_index, current_opts in enumerate(attempt_opts):
            try:
                info, filename = _run_download_attempt(job_id, url, current_opts)
                break
            except Exception as exc:
                last_error = exc

                if attempt_index == len(attempt_opts) - 1:
                    raise

                _set_job(
                    job_id,
                    status="retrying",
                    progress=0.0,
                    speed="",
                    eta="",
                    message="Retrying extractor...",
                )

        if info is None or filename is None:
            raise last_error or RuntimeError("Download failed")

        filename = _resolve_output_file(filename, format_choice, info)

        _set_job(
            job_id,
            status="completed",
            progress=100.0,
            speed="",
            eta="",
            message="Download complete",
            file_path=filename,
            file_name=Path(filename).name,
            title=info.get("title", "Untitled"),
            video_id=info.get("id"),
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
    failed = [job for job in _list_jobs() if job.get("status") == "error"]
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
    job = _get_job(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    return jsonify(job)


@app.get("/api/file/<job_id>")
def get_file(job_id: str):
    job = _get_job(job_id)
    if not job or job.get("status") != "completed":
        return abort(404)

    file_path = _resolve_job_file(job)
    if file_path is None:
        return abort(404)

    if job.get("file_path") != str(file_path):
        _set_job(job_id, file_path=str(file_path), file_name=file_path.name)

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
