
from types import SimpleNamespace

from app.retrieval import semantic_search as search_module


def test_semantic_search_applies_combined_ranking(monkeypatch):
    records = [
        {
            "external_id": "E1",
            "title": "Payment fraud detection",
            "text": "Payment fraud detection and transaction monitoring",
            "score": 0.80,
        },
        {
            "external_id": "E2",
            "title": "Customer service automation",
            "text": "Customer service automation",
            "score": 0.70,
        },
    ]

    class FakeClient:
        def query_points(self, **kwargs):
            return SimpleNamespace(
                points=[
                    SimpleNamespace(
                        payload={
                            **record,
                            "text": record["text"],
                        },
                        score=record["score"],
                    )
                    for record in records
                ]
            )

    monkeypatch.setattr(search_module, "ensure_collection", lambda: FakeClient())
    monkeypatch.setattr(
        search_module,
        "embed_query",
        lambda query: [0.1, 0.2],
    )

    result = search_module.semantic_search(
        query="payment fraud",
        limit=2,
    )

    assert len(result) == 2
    assert all("ranking_score" in item for item in result)
    assert all("ranking_components" in item for item in result)

    scores = [item["ranking_score"] for item in result]
    assert scores == sorted(scores, reverse=True)
