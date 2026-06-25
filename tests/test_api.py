from fastapi.testclient import TestClient

from app.main import app, store

client = TestClient(app)


def setup_function():
    # Reset to a known state before each test (store is process-global).
    store.set("NEW_UI", False)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_flags():
    r = client.get("/flags")
    assert r.status_code == 200
    assert {"name": "NEW_UI", "enabled": False} in r.json()


def test_get_new_ui():
    r = client.get("/flags/NEW_UI")
    assert r.status_code == 200
    assert r.json() == {"name": "NEW_UI", "enabled": False}


def test_get_unknown_flag_returns_404():
    r = client.get("/flags/NOPE")
    assert r.status_code == 404


def test_patch_set_true():
    r = client.patch("/flags/NEW_UI", json={"enabled": True})
    assert r.status_code == 200
    assert r.json() == {"name": "NEW_UI", "enabled": True}


def test_patch_toggle_when_enabled_omitted():
    r = client.patch("/flags/NEW_UI", json={})
    assert r.status_code == 200
    assert r.json()["enabled"] is True

    r = client.patch("/flags/NEW_UI", json={})
    assert r.json()["enabled"] is False


def test_patch_unknown_flag_returns_404():
    r = client.patch("/flags/NOPE", json={"enabled": True})
    assert r.status_code == 404
