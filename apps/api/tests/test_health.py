"""Health endpoint checks each dependency instead of assuming it (spec OBS-01, OBS-02)."""

import contextlib
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from decifra import main


class FakeQdrant:
    def get_collections(self):
        return SimpleNamespace(collections=[])


class FakeConnection:
    def execute(self, statement):
        return None


class FakePool:
    @contextlib.contextmanager
    def connection(self):
        yield FakeConnection()


def explode(*args, **kwargs):
    raise ConnectionError("unreachable")


@pytest.fixture
def healthy(monkeypatch):
    monkeypatch.setattr(main, "get_qdrant_client", lambda: FakeQdrant())
    monkeypatch.setattr(main, "get_pool", lambda: FakePool())
    monkeypatch.setattr(main, "get_settings", lambda: SimpleNamespace(openai_api_key="test"))
    return TestClient(main.app)


def test_every_dependency_up_answers_200(healthy):
    response = healthy.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["dependencies"] == {
        "qdrant": {"status": "ok"},
        "postgres": {"status": "ok"},
        "model": {"status": "ok"},
    }


def test_qdrant_down_answers_503_naming_it(healthy, monkeypatch):
    monkeypatch.setattr(main, "get_qdrant_client", explode)

    response = healthy.get("/health")

    assert response.status_code == 503
    assert response.json()["dependencies"]["qdrant"]["status"] == "down"
    assert response.json()["dependencies"]["postgres"]["status"] == "ok"


def test_postgres_down_answers_503_naming_it(healthy, monkeypatch):
    monkeypatch.setattr(main, "get_pool", explode)

    response = healthy.get("/health")

    assert response.status_code == 503
    assert response.json()["dependencies"]["postgres"]["status"] == "down"
    assert response.json()["dependencies"]["qdrant"]["status"] == "ok"


def test_missing_model_key_answers_503(healthy, monkeypatch):
    monkeypatch.setattr(main, "get_settings", lambda: SimpleNamespace(openai_api_key=""))

    response = healthy.get("/health")

    assert response.status_code == 503
    assert response.json()["dependencies"]["model"]["status"] == "down"
