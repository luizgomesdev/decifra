"""CORS origins come from the environment (spec DEP-04)."""

import importlib

from fastapi.testclient import TestClient

from decifra.config import Settings, get_settings


def app_with_origins(monkeypatch, value):
    monkeypatch.setenv("ALLOWED_ORIGINS", value)
    get_settings.cache_clear()
    return importlib.reload(importlib.import_module("decifra.main")).app


def preflight(app, origin):
    return TestClient(app).options(
        "/patients/p1/chat",
        headers={"Origin": origin, "Access-Control-Request-Method": "POST"},
    )


def test_origins_are_split_on_comma():
    settings = Settings(openai_api_key="test", allowed_origins="https://a.example, https://b.example")

    assert settings.origins == ["https://a.example", "https://b.example"]


def test_default_keeps_the_local_front(monkeypatch):
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    get_settings.cache_clear()

    assert get_settings().origins == ["http://localhost:5173"]


def test_configured_origin_is_allowed(monkeypatch):
    app = app_with_origins(monkeypatch, "https://demo.example")

    response = preflight(app, "https://demo.example")

    assert response.headers["access-control-allow-origin"] == "https://demo.example"


def test_unknown_origin_is_rejected(monkeypatch):
    app = app_with_origins(monkeypatch, "https://demo.example")

    response = preflight(app, "https://outro.example")

    assert "access-control-allow-origin" not in response.headers
