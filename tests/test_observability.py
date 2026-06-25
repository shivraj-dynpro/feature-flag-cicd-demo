from fastapi.testclient import TestClient
from prometheus_client import REGISTRY

from app.main import app, store

client = TestClient(app)


def _flag_changes(flag: str) -> float:
    value = REGISTRY.get_sample_value("feature_flag_changes_total", {"flag": flag})
    return value or 0.0


def test_metrics_endpoint_exposes_all_three_metrics():
    # Generate a little traffic first.
    client.get("/health")
    client.get("/flags/NEW_UI")
    client.patch("/flags/NEW_UI", json={"enabled": True})

    r = client.get("/metrics")
    assert r.status_code == 200
    body = r.text
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body
    assert "feature_flag_changes_total" in body


def test_request_id_header_is_added():
    r = client.get("/health")
    assert r.headers.get("X-Request-ID")


def test_request_id_is_echoed_when_supplied():
    r = client.get("/health", headers={"X-Request-ID": "demo-123"})
    assert r.headers.get("X-Request-ID") == "demo-123"


def test_flag_change_increments_counter():
    store.set("NEW_UI", False)
    before = _flag_changes("NEW_UI")
    client.patch("/flags/NEW_UI", json={"enabled": True})
    after = _flag_changes("NEW_UI")
    assert after == before + 1


def test_failed_flag_change_does_not_increment_counter():
    before = _flag_changes("NOPE")
    r = client.patch("/flags/NOPE", json={"enabled": True})
    assert r.status_code == 404
    after = _flag_changes("NOPE")
    assert after == before
