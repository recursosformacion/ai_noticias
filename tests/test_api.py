"""API interna de ai_noticias: acceso por token y contrato sin usuarios."""

from __future__ import annotations

from typing import Any, ClassVar

import pytest
from fastapi.testclient import TestClient

from app import api as api_module


class _Hit:
    def as_dict(self) -> dict[str, object]:
        return {"title": "Ave verum", "url": "https://example.org/ave"}


class _Response:
    hits: ClassVar[list[_Hit]] = [_Hit()]
    language: ClassVar[str] = "es"
    topics: ClassVar[list[str]] = ["coral"]


class _Connection:
    def close(self) -> None:
        return None


def test_news_api_requires_service_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OSAP_NEWS_API_TOKEN", "test-token")
    with TestClient(api_module.app) as client:
        response = client.get("/api/v1/news")
    assert response.status_code == 401


def test_news_api_returns_only_corpus(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OSAP_NEWS_API_TOKEN", "test-token")
    monkeypatch.setattr(api_module, "connect", lambda: _Connection())
    monkeypatch.setattr(
        api_module,
        "query_news",
        lambda *args, **kwargs: _Response(),
    )

    with TestClient(api_module.app) as client:
        response = client.get(
            "/api/v1/news?language=es&topics=coral&limit=5",
            headers={"X-OSAP-News-Token": "test-token"},
        )

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["items"][0]["title"] == "Ave verum"


def test_news_api_rejects_unknown_language(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OSAP_NEWS_API_TOKEN", "test-token")
    with TestClient(api_module.app) as client:
        response = client.get(
            "/api/v1/news?language=xx",
            headers={"X-OSAP-News-Token": "test-token"},
        )
    assert response.status_code == 400


def test_news_api_fails_closed_without_configured_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OSAP_NEWS_API_TOKEN", raising=False)
    with TestClient(api_module.app) as client:
        response = client.get("/api/v1/news/topics")
    assert response.status_code == 503


def test_news_api_does_not_expose_user_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OSAP_NEWS_API_TOKEN", "test-token")
    monkeypatch.setattr(api_module, "connect", lambda: _Connection())
    monkeypatch.setattr(api_module, "query_news", lambda *args, **kwargs: _Response())

    with TestClient(api_module.app) as client:
        data: dict[str, Any] = client.get(
            "/api/v1/news",
            headers={"X-OSAP-News-Token": "test-token"},
        ).json()

    assert "user_ref" not in data
    assert "email" not in data

