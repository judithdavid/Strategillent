
from typing import Any

import requests

from app.core.config import settings


TAVILY_SEARCH_URL = "https://api.tavily.com/search"
REQUEST_TIMEOUT_SECONDS = 20
MAX_RESULTS_LIMIT = 10


class WebResearchError(RuntimeError):
    """Raised when online research cannot be completed."""


def search_web(
    query: str,
    max_results: int = 5,
) -> list[dict[str, Any]]:
    """
    Search the public web and return normalised research results.

    Results are external candidates, not verified evidence.
    They are not persisted to the database by this function.
    """
    query = query.strip()

    if not query:
        raise ValueError("Search query cannot be empty.")

    if not 1 <= max_results <= MAX_RESULTS_LIMIT:
        raise ValueError(
            f"max_results must be between 1 and {MAX_RESULTS_LIMIT}."
        )

    api_key = settings.tavily_api_key.strip()

    if not api_key:
        raise WebResearchError(
            "Tavily API key is not configured."
        )

    payload = {
        "api_key": api_key,
        "query": query,
        "topic": "general",
        "search_depth": "basic",
        "max_results": max_results,
        "include_answer": False,
    }

    try:
        response = requests.post(
            TAVILY_SEARCH_URL,
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()

    except requests.RequestException as exc:
        raise WebResearchError(
            "Online research request failed."
        ) from exc

    except ValueError as exc:
        raise WebResearchError(
            "Online research returned invalid JSON."
        ) from exc

    raw_results = data.get("results", [])

    if not isinstance(raw_results, list):
        raise WebResearchError(
            "Online research returned an invalid results format."
        )

    results = []

    for item in raw_results:
        if not isinstance(item, dict):
            continue

        title = item.get("title")
        url = item.get("url")
        content = item.get("content")

        if not isinstance(title, str) or not title.strip():
            continue

        if not isinstance(url, str) or not url.startswith(
            ("https://", "http://")
        ):
            continue

        if not isinstance(content, str):
            content = ""

        results.append(
            {
                "title": title.strip(),
                "url": url.strip(),
                "content": content.strip(),
                "published_date": item.get("published_date"),
                "score": item.get("score"),
                "source_type": "web_search",
                "query": query,
            }
        )

    return results[:max_results]
