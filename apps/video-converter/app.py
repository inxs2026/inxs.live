import json
import os
import shutil
import subprocess
import threading
import uuid
from pathlib import Path
from typing import Dict

from flask import Flask, jsonify, render_template, request, send_file, send_from_directory
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

app = Flask(__name__)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(app.static_folder, "favicon.ico", mimetype="image/vnd.microsoft.icon")

SUPPORTED_FORMATS = ["mp4", "mkv", "avi", "mov", "webm", "flv", "wmv", "m4v"]
QUALITY_PRESETS = {
    "fast": {"x264_preset": "veryfast", "x264_crf": "30", "vp9_crf": "40"},
    "balanced": {"x264_preset": "medium", "x264_crf": "24", "vp9_crf": "32"},
    "high": {"x264_preset": "slow", "x264_crf": "18", "vp9_crf": "24"},
}
PLATFORM_PRESETS = {
    "none": {"label": "Custom"},
    "youtube_1080p": {"label": "YouTube 1080p"},
    "instagram": {"label": "Instagram"},
    "whatsapp": {"label": "WhatsApp"},
}
BASE_DIR = Path(__file__).resolve().parent
MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "100"))
DIRECT_UPLOAD_MB = min(
    int(os.environ.get("DIRECT_UPLOAD_MB", str(max(MAX_UPLOAD_MB - 5, 1)))),
    MAX_UPLOAD_MB,
)
CHUNK_UPLOAD_MB = max(1, min(int(os.environ.get("CHUNK_UPLOAD_MB", "24")), MAX_UPLOAD_MB))
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024


def resolve_storage_dir(env_name: str, default_path: Path) -> Path:
    configured_path = os.environ.get(env_name)
    directory = Path(configured_path).expanduser() if configured_path else default_path
    directory.mkdir(parents=True, exist_ok=True)

    if not os.access(directory, os.W_OK):
        raise RuntimeError(f"{env_name} is not writable: {directory}")

    return directory


def missing_dependencies() -> list[str]:
    return [name for name in ("ffmpeg", "ffprobe") if shutil.which(name) is None]


DOWNLOADS_DIR = resolve_storage_dir("DOWNLOAD_DIR", BASE_DIR / "downloads")
UPLOADS_DIR = resolve_storage_dir("UPLOADS_DIR", BASE_DIR / "uploads")
CHUNK_UPLOADS_DIR = resolve_storage_dir("CHUNK_UPLOADS_DIR", UPLOADS_DIR / "chunks")

jobs_lock = threading.Lock()
jobs: Dict[str, Dict[str, str]] = {}
job_processes: Dict[str, subprocess.Popen] = {}


def is_valid_upload_id(upload_id: str) -> bool:
    sanitized = upload_id.replace("-", "")
    return bool(sanitized) and sanitized.isalnum()


def get_upload_dir(upload_id: str) -> Path:
    return CHUNK_UPLOADS_DIR / upload_id


def get_upload_manifest_path(upload_id: str) -> Path:
    return get_upload_dir(upload_id) / "manifest.json"


def cleanup_upload(upload_id: str) -> None:
    shutil.rmtree(get_upload_dir(upload_id), ignore_errors=True)


def load_upload_manifest(upload_id: str) -> dict:
    manifest_path = get_upload_manifest_path(upload_id)
    if not manifest_path.exists():
        raise RuntimeError("Upload session not found")

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("Upload session is corrupt") from exc

    if not isinstance(payload, dict):
        raise RuntimeError("Upload session is invalid")

    return payload


def save_upload_manifest(upload_id: str, filename: str, total_chunks: int) -> None:
    upload_dir = get_upload_dir(upload_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = get_upload_manifest_path(upload_id)
    manifest = {"filename": filename, "total_chunks": total_chunks}
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


def assemble_upload(upload_id: str, destination: Path) -> str:
    manifest = load_upload_manifest(upload_id)
    filename = manifest.get("filename", "")
    total_chunks = int(manifest.get("total_chunks") or 0)
    upload_dir = get_upload_dir(upload_id)

    if total_chunks <= 0:
        raise RuntimeError("Upload session is incomplete")

    with destination.open("wb") as output_handle:
        for chunk_index in range(total_chunks):
            chunk_path = upload_dir / f"{chunk_index:06d}.part"
            if not chunk_path.exists():
                raise RuntimeError(f"Missing upload chunk {chunk_index + 1} of {total_chunks}")

            with chunk_path.open("rb") as input_handle:
                shutil.copyfileobj(input_handle, output_handle)

    cleanup_upload(upload_id)
    return filename


def probe_duration_seconds(input_path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(input_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Failed to probe video duration")

    try:
        return max(float(result.stdout.strip()), 0.0)
    except ValueError as exc:
        raise RuntimeError("Could not parse video duration") from exc


def parse_progress_timestamp(raw_value: str) -> int | None:
    value = raw_value.strip()
    if not value or value.upper() == "N/A":
        return None

    try:
        return int(value)
    except ValueError:
        return None


def set_job(job_id: str, **fields: str) -> None:
    with jobs_lock:
        if job_id in jobs:
            jobs[job_id].update(fields)


def get_job_status(job_id: str) -> str:
    with jobs_lock:
        job = jobs.get(job_id, {})
        return job.get("status", "")


def set_job_process(job_id: str, process: subprocess.Popen | None) -> None:
    with jobs_lock:
        if process is None:
            job_processes.pop(job_id, None)
        else:
            job_processes[job_id] = process


def build_video_args(output_format: str, quality_preset: str, platform_preset: str) -> list[str]:
    if platform_preset == "youtube_1080p":
        return [
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-vf",
            "scale='min(1920,iw)':'min(1080,ih)':force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-r",
            "30",
            "-maxrate",
            "8M",
            "-bufsize",
            "16M",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-movflags",
            "+faststart",
        ]

    if platform_preset == "instagram":
        return [
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "23",
            "-vf",
            "scale='min(1080,iw)':'min(1350,ih)':force_original_aspect_ratio=decrease,format=yuv420p",
            "-r",
            "30",
            "-maxrate",
            "5M",
            "-bufsize",
            "10M",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-ar",
            "44100",
            "-movflags",
            "+faststart",
        ]

    if platform_preset == "whatsapp":
        return [
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "30",
            "-vf",
            "scale='min(854,iw)':'min(480,ih)':force_original_aspect_ratio=decrease,format=yuv420p",
            "-r",
            "24",
            "-maxrate",
            "900k",
            "-bufsize",
            "1800k",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-ar",
            "32000",
            "-movflags",
            "+faststart",
        ]

    preset_cfg = QUALITY_PRESETS.get(quality_preset, QUALITY_PRESETS["balanced"])

    if output_format in {"mp4", "mkv", "mov", "m4v"}:
        return [
            "-c:v",
            "libx264",
            "-preset",
            preset_cfg["x264_preset"],
            "-crf",
            preset_cfg["x264_crf"],
            "-c:a",
            "aac",
            "-b:a",
            "192k",
        ]

    if output_format == "webm":
        return [
            "-c:v",
            "libvpx-vp9",
            "-crf",
            preset_cfg["vp9_crf"],
            "-b:v",
            "0",
            "-c:a",
            "libopus",
            "-b:a",
            "128k",
        ]

    # Keep ffmpeg defaults for legacy containers where explicit codecs can break.
    return []


def get_unique_output_path(base_name: str, output_format: str) -> Path:
    candidate = DOWNLOADS_DIR / f"{base_name}_converted.{output_format}"
    if not candidate.exists():
        return candidate

    idx = 1
    while True:
        candidate = DOWNLOADS_DIR / f"{base_name}_converted_{idx}.{output_format}"
        if not candidate.exists():
            return candidate
        idx += 1


def convert_job(
    job_id: str,
    input_path: Path,
    output_format: str,
    quality_preset: str,
    platform_preset: str,
    original_stem: str,
) -> None:
    output_path = get_unique_output_path(original_stem, output_format)
    output_name = output_path.name
    temp_path = UPLOADS_DIR / f"{job_id}_output.{output_format}"
    process: subprocess.Popen | None = None

    try:
        duration_seconds = probe_duration_seconds(input_path)
        video_args = build_video_args(output_format, quality_preset, platform_preset)
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            *video_args,
            "-progress",
            "pipe:1",
            "-nostats",
            str(temp_path),
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True,
            bufsize=1,
        )
        set_job_process(job_id, process)

        assert process.stdout is not None
        for line in process.stdout:
            if get_job_status(job_id) == "cancelling":
                process.terminate()
                break

            line = line.strip()
            if line.startswith("out_time_ms=") and duration_seconds > 0:
                out_time_ms = parse_progress_timestamp(line.split("=", 1)[1])
                if out_time_ms is None:
                    continue
                percent = min((out_time_ms / (duration_seconds * 1_000_000)) * 100, 100)
                set_job(job_id, progress=f"{percent:.2f}", status="running")
            elif line.startswith("progress=end"):
                set_job(job_id, progress="100", status="running")

        process.wait()
        status_now = get_job_status(job_id)
        if status_now == "cancelling":
            set_job(job_id, status="cancelled", message="Conversion cancelled by user")
            return

        if process.returncode != 0 or not temp_path.exists():
            raise RuntimeError("ffmpeg failed during conversion")

        shutil.move(str(temp_path), str(output_path))
        set_job(
            job_id,
            progress="100",
            status="done",
            output_path=str(output_path),
            output_name=output_name,
            message=f"Saved to {output_path}",
        )
    except Exception as exc:
        set_job(job_id, status="error", message=str(exc))
    finally:
        set_job_process(job_id, None)
        if input_path.exists():
            input_path.unlink(missing_ok=True)
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)


def prepare_uploaded_job(
    job_id: str,
    upload_id: str,
    filename: str,
    output_format: str,
    quality_preset: str,
    platform_preset: str,
    original_stem: str,
) -> None:
    input_path = UPLOADS_DIR / f"{job_id}_{filename}"

    try:
        set_job(job_id, status="preparing", message="Assembling upload", progress="0")
        assemble_upload(upload_id, input_path)
    except Exception as exc:
        cleanup_upload(upload_id)
        input_path.unlink(missing_ok=True)
        set_job(job_id, status="error", message=str(exc))
        return

    convert_job(job_id, input_path, output_format, quality_preset, platform_preset, original_stem)


@app.get("/")
def index():
    return render_template(
        "index.html",
        formats=SUPPORTED_FORMATS,
        quality_presets=list(QUALITY_PRESETS.keys()),
        platform_presets=PLATFORM_PRESETS,
        max_upload_mb=MAX_UPLOAD_MB,
        direct_upload_mb=DIRECT_UPLOAD_MB,
        chunk_upload_mb=CHUNK_UPLOAD_MB,
    )


@app.errorhandler(RequestEntityTooLarge)
def handle_request_too_large(_exc: RequestEntityTooLarge):
    return jsonify({"error": f"File exceeds the {MAX_UPLOAD_MB} MB upload limit"}), 413


@app.post("/api/upload-chunk")
def upload_chunk():
    if "chunk" not in request.files:
        return jsonify({"error": "No chunk provided"}), 400

    upload_id = (request.form.get("upload_id") or "").strip()
    filename = secure_filename(request.form.get("filename") or "")

    try:
        chunk_index = int(request.form.get("chunk_index") or "-1")
        total_chunks = int(request.form.get("total_chunks") or "0")
    except ValueError:
        return jsonify({"error": "Invalid chunk metadata"}), 400

    if not is_valid_upload_id(upload_id):
        return jsonify({"error": "Invalid upload id"}), 400

    if not filename:
        return jsonify({"error": "Invalid filename"}), 400

    if total_chunks <= 0 or chunk_index < 0 or chunk_index >= total_chunks:
        return jsonify({"error": "Invalid chunk numbering"}), 400

    input_ext = Path(filename).suffix.lower().lstrip(".")
    if input_ext and input_ext not in SUPPORTED_FORMATS:
        return jsonify({"error": f"Unsupported input format: {input_ext}"}), 400

    upload_dir = get_upload_dir(upload_id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = get_upload_manifest_path(upload_id)
    if manifest_path.exists():
        try:
            manifest = load_upload_manifest(upload_id)
        except RuntimeError as exc:
            return jsonify({"error": str(exc)}), 400
        if manifest.get("filename") != filename or int(manifest.get("total_chunks") or 0) != total_chunks:
            return jsonify({"error": "Upload session does not match file metadata"}), 400
    else:
        save_upload_manifest(upload_id, filename, total_chunks)

    chunk = request.files["chunk"]
    chunk_path = upload_dir / f"{chunk_index:06d}.part"
    chunk.save(chunk_path)

    return jsonify({"ok": True, "chunk_index": chunk_index, "total_chunks": total_chunks})


@app.post("/api/cancel-upload/<upload_id>")
def cancel_upload(upload_id: str):
    if not is_valid_upload_id(upload_id):
        return jsonify({"error": "Invalid upload id"}), 400

    cleanup_upload(upload_id)
    return jsonify({"status": "cancelled"}), 200


@app.get("/healthz")
def healthcheck():
    missing = missing_dependencies()
    if missing:
        return jsonify({"status": "error", "missing": missing}), 503

    return jsonify({"status": "ok"})


@app.post("/api/convert")
def start_convert():
    missing = missing_dependencies()
    if missing:
        return jsonify({"error": f"Missing required dependencies: {', '.join(missing)}"}), 503

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    output_format = (request.form.get("output_format") or "").lower().strip()
    quality_preset = (request.form.get("quality_preset") or "balanced").lower().strip()
    platform_preset = (request.form.get("platform_preset") or "none").lower().strip()

    if not file.filename:
        return jsonify({"error": "Please choose a file"}), 400

    if output_format not in SUPPORTED_FORMATS:
        return jsonify({"error": "Invalid output format"}), 400

    if quality_preset not in QUALITY_PRESETS:
        return jsonify({"error": "Invalid quality preset"}), 400

    if platform_preset not in PLATFORM_PRESETS:
        return jsonify({"error": "Invalid platform preset"}), 400

    if platform_preset != "none":
        output_format = "mp4"

    filename = secure_filename(file.filename)
    if not filename:
        return jsonify({"error": "Invalid filename"}), 400

    input_ext = Path(filename).suffix.lower().lstrip(".")
    if input_ext and input_ext not in SUPPORTED_FORMATS:
        return jsonify({"error": f"Unsupported input format: {input_ext}"}), 400

    job_id = uuid.uuid4().hex
    stem = Path(filename).stem
    input_path = UPLOADS_DIR / f"{job_id}_{filename}"
    file.save(input_path)

    with jobs_lock:
        jobs[job_id] = {
            "status": "queued",
            "progress": "0",
            "message": "Queued",
            "output_path": "",
            "output_name": "",
        }

    thread = threading.Thread(
        target=convert_job,
        args=(job_id, input_path, output_format, quality_preset, platform_preset, stem),
        daemon=True,
    )
    thread.start()

    return jsonify({"job_id": job_id})


@app.post("/api/complete-upload")
def complete_upload():
    missing = missing_dependencies()
    if missing:
        return jsonify({"error": f"Missing required dependencies: {', '.join(missing)}"}), 503

    upload_id = (request.form.get("upload_id") or "").strip()
    filename = secure_filename(request.form.get("filename") or "")
    output_format = (request.form.get("output_format") or "").lower().strip()
    quality_preset = (request.form.get("quality_preset") or "balanced").lower().strip()
    platform_preset = (request.form.get("platform_preset") or "none").lower().strip()

    if not is_valid_upload_id(upload_id):
        return jsonify({"error": "Invalid upload id"}), 400

    if not filename:
        return jsonify({"error": "Invalid filename"}), 400

    if output_format not in SUPPORTED_FORMATS:
        return jsonify({"error": "Invalid output format"}), 400

    if quality_preset not in QUALITY_PRESETS:
        return jsonify({"error": "Invalid quality preset"}), 400

    if platform_preset not in PLATFORM_PRESETS:
        return jsonify({"error": "Invalid platform preset"}), 400

    if platform_preset != "none":
        output_format = "mp4"

    try:
        manifest = load_upload_manifest(upload_id)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 400

    if manifest.get("filename") != filename:
        return jsonify({"error": "Upload metadata mismatch"}), 400

    job_id = uuid.uuid4().hex
    stem = Path(filename).stem

    with jobs_lock:
        jobs[job_id] = {
            "status": "queued",
            "progress": "0",
            "message": "Queued",
            "output_path": "",
            "output_name": "",
        }

    thread = threading.Thread(
        target=prepare_uploaded_job,
        args=(job_id, upload_id, filename, output_format, quality_preset, platform_preset, stem),
        daemon=True,
    )
    thread.start()

    return jsonify({"job_id": job_id})


@app.get("/api/progress/<job_id>")
def get_progress(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)

    if not job:
        return jsonify({"error": "Job not found"}), 404

    return jsonify(job)


@app.post("/api/cancel/<job_id>")
def cancel_job(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
        process = job_processes.get(job_id)

    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job.get("status") in {"done", "error", "cancelled"}:
        return jsonify({"status": job.get("status"), "message": "Job already finished"}), 200

    set_job(job_id, status="cancelling", message="Cancelling conversion...")

    if process and process.poll() is None:
        process.terminate()

    return jsonify({"status": "cancelling"}), 200


@app.get("/api/download/<job_id>")
def download_output(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)

    if not job or job.get("status") != "done":
        return jsonify({"error": "Output not ready"}), 404

    output_path = Path(job["output_path"])
    if not output_path.exists():
        return jsonify({"error": "Converted file missing"}), 404

    return send_file(output_path, as_attachment=True, download_name=job.get("output_name") or output_path.name)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "3000"))
    host = os.environ.get("HOST", "127.0.0.1")
    print(f"Starting server on http://localhost:{port}")
    app.run(host=host, port=port, debug=False)
