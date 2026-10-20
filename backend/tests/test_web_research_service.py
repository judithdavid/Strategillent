
import pytest
import requests

from app.services import web_research_service as research


def test_search_web_normalises_results(monkeypatch):
    monkeypatch.setattr(
        research.settings,
        "tavily_api_key",
        "test-key",
    )

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "results": [
                    {
                        "title": "Fraud Detection Research",
                        "url": "https://example.com/fraud",
                        "content": "Research about fraud detection.",
                        "published_date": "2026-01-01",
                        "score": 0.95,
                    }
                ]
            }

    def fake_post(url, json, timeout):
        assert url == research.TAVILY_SEARCH_URL
        assert json["api_key"] == "test-key"
        assert json["query"] == "fraud detection"
        assert timeout == research.REQUEST_TIMEOUT_SECONDS
        return FakeResponse()

    monkeypatch.setattr(research.requests, "post", fake_post)

    results = research.search_web("fraud detection")

    assert len(results) == 1
    assert results[0]["title"] == "Fraud Detection Research"
    assert results[0]["url"] == "https://example.com/fraud"
    assert results[0]["source_type"] == "web_search"
    assert results[0]["query"] == "fraud detection"


def test_search_web_rejects_empty_query():
    with pytest.raises(ValueError):
        research.search_web("   ")


def test_search_web_rejects_invalid_result_limit():
    with pytest.raises(ValueError):
        research.search_web("fraud detection", max_results=11)


def test_search_web_requires_api_key(monkeypatch):
    monkeypatch.setattr(
        research.settings,
        "tavily_api_key",
        "",
    )

    with pytest.raises(research.WebResearchError):
        research.search_web("fraud detection")


def test_search_web_handles_http_failure(monkeypatch):
    monkeypatch.setattr(
        research.settings,
        "tavily_api_key",
        "test-key",
    )

    def fake_post(*args, **kwargs):
        raise requests.Timeout("simulated timeout")

    monkeypatch.setattr(research.requests, "post", fake_post)

    with pytest.raises(research.WebResearchError):
        research.search_web("fraud detection")
