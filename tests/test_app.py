import os
import tempfile
import pytest
import app as application

@pytest.fixture()
def client(monkeypatch):
    fd, path = tempfile.mkstemp()
    os.close(fd)
    monkeypatch.setattr(application, "DB_PATH", path)
    application.init_db()
    with application.app.test_client() as client:
        yield client
    os.remove(path)

def test_unique_record_is_saved(client):
    response = client.post("/api/records", json={"content": "Alpha customer record"})
    assert response.status_code == 201
    assert response.get_json()["status"] == "accepted"

def test_exact_duplicate_is_rejected(client):
    client.post("/api/records", json={"content": "Alpha customer record"})
    response = client.post("/api/records", json={"content": " alpha   customer record "})
    assert response.status_code == 409
    assert response.get_json()["reason"] == "redundant"

def test_empty_content_is_rejected(client):
    response = client.post("/api/records", json={"content": ""})
    assert response.status_code == 400
