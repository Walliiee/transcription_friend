from io import BytesIO

import pytest

from scripts import web_api
from scripts.web_api import app, sanitize_filename, strip_timestamps


@pytest.fixture(autouse=True)
def clear_jobs_state():
    with web_api.jobs_lock:
        web_api.jobs.clear()
    yield
    with web_api.jobs_lock:
        web_api.jobs.clear()


def test_sanitize_filename():
    assert sanitize_filename("my file?.m4a") == "my_file_.m4a"


def test_strip_timestamps():
    text = "[00:00:01] Hello\n[00:00:02] world"
    assert strip_timestamps(text) == "Hello\nworld"


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["ok"] is True


def test_transcription_endpoint_requires_file():
    client = app.test_client()
    response = client.post("/api/transcriptions", data={})
    assert response.status_code == 400


def test_transcription_endpoint_rejects_bad_extension():
    client = app.test_client()
    response = client.post(
        "/api/transcriptions",
        data={"audio": (BytesIO(b"fake"), "audio.txt"), "preset": "balanced", "language": "en"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400


def test_process_job_marks_failed_on_exception(monkeypatch):
    job_id = "job-failure-test"
    with web_api.jobs_lock:
        web_api.jobs[job_id] = {
            "id": job_id,
            "status": "queued",
            "progress": 10,
            "message": "Queued",
            "created_at": web_api.now_iso(),
            "updated_at": web_api.now_iso(),
            "source_name": "a.m4a",
            "source_stem": "a",
            "upload_path": "/tmp/does-not-matter.m4a",
            "preset": "balanced",
            "model_size": "small",
            "language": "en",
            "auto_detect": True,
            "postprocess": False,
            "device": "cpu",
            "estimate_seconds": 30,
        }

    def fail_model_load(model_size, device_preference):
        raise RuntimeError("boom")

    monkeypatch.setattr(web_api, "get_or_load_model", fail_model_load)
    web_api.process_job(job_id)

    with web_api.jobs_lock:
        job = web_api.jobs[job_id]
    assert job["status"] == "failed"
    assert "boom" in job["error"]


def test_get_transcription_status_handles_naive_timestamp():
    client = app.test_client()
    job_id = "job-naive-time"
    with web_api.jobs_lock:
        web_api.jobs[job_id] = {
            "id": job_id,
            "status": "queued",
            "progress": 10,
            "message": "Queued",
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:00",
            "source_name": "a.m4a",
            "source_stem": "a",
            "upload_path": "/tmp/a.m4a",
            "preset": "balanced",
            "model_size": "small",
            "language": "en",
            "auto_detect": True,
            "postprocess": False,
            "device": "cpu",
            "estimate_seconds": 30,
        }

    response = client.get(f"/api/transcriptions/{job_id}")
    assert response.status_code == 200


def test_recent_jobs_sorts_with_valid_datetimes():
    client = app.test_client()
    with web_api.jobs_lock:
        web_api.jobs["recent-a"] = {
            "id": "recent-a",
            "status": "completed",
            "progress": 100,
            "message": "Done",
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-01T00:00:00+00:00",
            "source_name": "a.m4a",
            "source_stem": "a",
            "upload_path": "/tmp/a.m4a",
            "preset": "balanced",
            "model_size": "small",
            "language": "en",
            "auto_detect": True,
            "postprocess": False,
            "device": "cpu",
            "estimate_seconds": 30,
        }
        web_api.jobs["recent-b"] = {
            "id": "recent-b",
            "status": "completed",
            "progress": 100,
            "message": "Done",
            "created_at": "2026-02-01T00:00:00+00:00",
            "updated_at": "2026-02-01T00:00:00+00:00",
            "source_name": "b.m4a",
            "source_stem": "b",
            "upload_path": "/tmp/b.m4a",
            "preset": "fast",
            "model_size": "tiny",
            "language": "en",
            "auto_detect": False,
            "postprocess": False,
            "device": "cpu",
            "estimate_seconds": 20,
        }

    response = client.get("/api/transcriptions/recent")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload[0]["job_id"] == "recent-b"
