from io import BytesIO

from scripts.web_api import app, sanitize_filename, strip_timestamps


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
