#!/usr/bin/env python3
"""
Local web API for server-backed transcription.

Intended for local, single-instance use (not a production job queue).

Run:
    python scripts/web_api.py --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

import argparse
import json
import re
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_from_directory

import config
from utils.corrections import get_corrections
from utils.whisper_helpers import load_model, transcribe_file

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
RUNTIME_DIR = Path(tempfile.gettempdir()) / "transcription_friend_web"
UPLOAD_DIR = RUNTIME_DIR / "uploads"
RESULTS_DIR = RUNTIME_DIR / "results"
MAX_UPLOAD_BYTES = 200 * 1024 * 1024
ALLOWED_EXTENSIONS = {".m4a", ".mp3", ".wav", ".mp4", ".m4b", ".aac", ".flac", ".ogg"}
JOB_TIMEOUT_SECONDS = 60 * 60

MODEL_PRESETS = {
    "fast": "tiny",
    "balanced": "small",
    "best": "medium",
}

jobs: dict[str, dict[str, Any]] = {}
jobs_lock = threading.Lock()
models: dict[str, Any] = {}
models_lock = threading.Lock()

app = Flask(__name__, static_folder=str(DOCS_DIR), static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", name).strip("._")
    return cleaned or "audio"


def strip_timestamps(text: str) -> str:
    return re.sub(r"^\[\d{2}:\d{2}:\d{2}\]\s*", "", text, flags=re.MULTILINE)


def clean_formatting(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s+([,.])", r"\1", text)
    text = re.sub(r"\[(\d{2}:\d{2}:\d{2})\]([^\s])", r"[\1] \2", text)
    return text.strip()


def apply_text_corrections(text: str, language: str) -> str:
    corrected = text
    for wrong, correct in get_corrections(language).items():
        corrected = corrected.replace(wrong, correct)
    return clean_formatting(corrected)


def estimate_seconds(file_size_bytes: int, preset: str) -> int:
    mb = max(1, file_size_bytes // (1024 * 1024))
    multiplier = {"fast": 2, "balanced": 4, "best": 7}.get(preset, 4)
    return int(max(30, mb * multiplier))


def get_or_load_model(model_size: str, device_preference: str):
    key = f"{model_size}:{device_preference}"
    with models_lock:
        if key in models:
            return models[key]
    model, device_used = load_model(
        model_size=model_size,
        device_preference=device_preference,
        gpu_compute_type=config.GPU_COMPUTE_TYPE,
        cpu_compute_type=config.CPU_COMPUTE_TYPE,
    )
    with models_lock:
        models[key] = (model, device_used)
    return model, device_used


def update_job(job_id: str, **updates: Any) -> None:
    with jobs_lock:
        job = jobs[job_id]
        job.update(updates)
        job["updated_at"] = now_iso()


def process_job(job_id: str) -> None:
    with jobs_lock:
        job = dict(jobs[job_id])

    start = datetime.now(timezone.utc)
    try:
        update_job(job_id, status="loading_model", progress=20, message="Loading Whisper model")
        model, device_used = get_or_load_model(job["model_size"], job["device"])
        update_job(
            job_id,
            status="transcribing",
            progress=50,
            message=f"Transcribing on {device_used}",
            device_used=device_used,
        )

        language = None if job["auto_detect"] else job["language"]
        timestamped_text, info = transcribe_file(
            model,
            job["upload_path"],
            language=language,
            beam_size=config.BEAM_SIZE,
            vad_filter=config.VAD_FILTER,
            word_timestamps=True,
        )

        plain_text = strip_timestamps(timestamped_text)
        if job["postprocess"]:
            update_job(job_id, status="postprocessing", progress=80, message="Applying corrections")
            plain_text = apply_text_corrections(plain_text, info["language"])
            timestamped_text = clean_formatting(timestamped_text)

        plain_path = RESULTS_DIR / f"{job_id}_transcript.txt"
        time_path = RESULTS_DIR / f"{job_id}_transcript_timestamped.txt"
        plain_path.write_text(plain_text, encoding="utf-8")
        time_path.write_text(timestamped_text, encoding="utf-8")

        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        update_job(
            job_id,
            status="completed",
            progress=100,
            message="Done",
            transcript=plain_text,
            timestamped_transcript=timestamped_text,
            transcript_path=str(plain_path),
            timestamped_path=str(time_path),
            detected_language=info["language"],
            audio_duration_seconds=info["duration"],
            elapsed_seconds=elapsed,
        )
    except Exception as exc:
        update_job(job_id, status="failed", progress=100, message="Failed", error=str(exc))


@app.route("/")
def root():
    return send_from_directory(DOCS_DIR, "index.html")


@app.route("/api/health")
def health():
    return jsonify({"ok": True, "time": now_iso()})


@app.route("/api/transcriptions", methods=["POST"])
def create_transcription():
    audio = request.files.get("audio")
    if audio is None or not audio.filename:
        return jsonify({"error": "No audio file provided"}), 400

    ext = Path(audio.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"Unsupported format: {ext or 'unknown'}"}), 400

    preset = request.form.get("preset", "balanced")
    if preset not in MODEL_PRESETS:
        return jsonify({"error": "Invalid preset"}), 400

    model_size = request.form.get("model_size") or MODEL_PRESETS[preset]
    if model_size not in {"tiny", "base", "small", "medium", "large"}:
        return jsonify({"error": "Invalid model size"}), 400

    language = request.form.get("language", config.DEFAULT_LANGUAGE)
    if language not in config.SUPPORTED_LANGUAGES:
        return jsonify({"error": "Invalid language"}), 400

    auto_detect = request.form.get("auto_detect", "false").lower() == "true"
    postprocess = request.form.get("postprocess", "true").lower() == "true"
    device = request.form.get("device", config.DEFAULT_DEVICE)
    if device not in {"cpu", "cuda"}:
        return jsonify({"error": "Invalid device"}), 400

    job_id = uuid.uuid4().hex
    filename = sanitize_filename(audio.filename)
    source_stem = Path(filename).stem
    upload_path = UPLOAD_DIR / f"{job_id}.upload"
    audio.save(upload_path)
    file_size = upload_path.stat().st_size

    job = {
        "id": job_id,
        "status": "queued",
        "progress": 10,
        "message": "Queued",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "source_name": filename,
        "source_stem": source_stem,
        "upload_path": str(upload_path),
        "preset": preset,
        "model_size": model_size,
        "language": language,
        "auto_detect": auto_detect,
        "postprocess": postprocess,
        "device": device,
        "estimate_seconds": estimate_seconds(file_size, preset),
    }

    with jobs_lock:
        jobs[job_id] = job

    worker = threading.Thread(target=process_job, args=(job_id,), daemon=True)
    worker.start()

    return jsonify(
        {
            "job_id": job_id,
            "status": "queued",
            "estimate_seconds": job["estimate_seconds"],
            "max_upload_mb": MAX_UPLOAD_BYTES // (1024 * 1024),
        }
    )


@app.route("/api/transcriptions/<job_id>", methods=["GET"])
def get_transcription_status(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
    if job is None:
        return jsonify({"error": "Job not found"}), 404

    created = parse_iso_datetime(job["created_at"])
    age_seconds = (datetime.now(timezone.utc) - created).total_seconds()
    timed_out = age_seconds > JOB_TIMEOUT_SECONDS and job["status"] not in {"completed", "failed"}
    if timed_out:
        update_job(job_id, status="failed", message="Timed out", error="Job exceeded timeout")
        with jobs_lock:
            job = jobs[job_id]

    payload = {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"],
        "source_name": job["source_name"],
        "preset": job["preset"],
        "model_size": job["model_size"],
        "created_at": job["created_at"],
        "updated_at": job["updated_at"],
    }
    if job["status"] == "completed":
        payload.update(
            {
                "detected_language": job.get("detected_language"),
                "audio_duration_seconds": job.get("audio_duration_seconds"),
                "elapsed_seconds": job.get("elapsed_seconds"),
            }
        )
    if job["status"] == "failed":
        payload["error"] = job.get("error", "Unknown error")
    return jsonify(payload)


@app.route("/api/transcriptions/<job_id>/result", methods=["GET"])
def get_transcription_result(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
    if job is None:
        return jsonify({"error": "Job not found"}), 404
    if job["status"] != "completed":
        return jsonify({"error": "Job is not completed"}), 409

    include_timestamps = request.args.get("timestamps", "false").lower() == "true"
    text = job["timestamped_transcript"] if include_timestamps else job["transcript"]
    return jsonify(
        {
            "job_id": job_id,
            "transcript": text,
            "detected_language": job.get("detected_language"),
            "audio_duration_seconds": job.get("audio_duration_seconds"),
            "elapsed_seconds": job.get("elapsed_seconds"),
            "timestamps": include_timestamps,
        }
    )


@app.route("/api/transcriptions/<job_id>/download", methods=["GET"])
def download_transcription(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
    if job is None:
        return jsonify({"error": "Job not found"}), 404
    if job["status"] != "completed":
        return jsonify({"error": "Job is not completed"}), 409

    include_timestamps = request.args.get("timestamps", "false").lower() == "true"
    path = Path(job["timestamped_path"] if include_timestamps else job["transcript_path"])
    return send_from_directory(path.parent, path.name, as_attachment=True)


@app.route("/api/transcriptions/recent", methods=["GET"])
def recent_jobs():
    with jobs_lock:
        ordered = sorted(
            jobs.values(),
            key=lambda x: parse_iso_datetime(x["created_at"]),
            reverse=True,
        )[:10]
    return jsonify(
        [
            {
                "job_id": job["id"],
                "status": job["status"],
                "source_name": job["source_name"],
                "created_at": job["created_at"],
                "model_size": job["model_size"],
                "language": "auto" if job["auto_detect"] else job["language"],
            }
            for job in ordered
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local transcription web API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def main() -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    args = parse_args()
    print(json.dumps({"host": args.host, "port": args.port, "runtime_dir": str(RUNTIME_DIR)}))
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
