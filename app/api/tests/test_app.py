"""Tests unitaires : la base de données est simulée, aucun PostgreSQL requis."""
import psycopg
import pytest

import app as api


@pytest.fixture
def client():
    api.app.config["TESTING"] = True
    return api.app.test_client()


def test_health_does_not_need_database(client, monkeypatch):
    def fail():
        raise psycopg.OperationalError("db down")

    monkeypatch.setattr(api, "get_conn", fail)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_ready_returns_503_when_database_is_down(client, monkeypatch):
    def fail():
        raise psycopg.OperationalError("db down")

    monkeypatch.setattr(api, "get_conn", fail)
    assert client.get("/ready").status_code == 503


def test_metrics_exposes_request_counter(client):
    client.get("/health")
    body = client.get("/metrics").get_data(as_text=True)
    assert 'http_requests_total{endpoint="/health",method="GET",status="200"}' in body


def test_create_item_rejects_empty_name(client):
    resp = client.post("/api/items", json={"name": "   "})
    assert resp.status_code == 400
