# from fastapi.testclient import TestClient

# from app.main import app


# client = TestClient(app)


# def test_question_endpoint():
#     payload = {
#         "question": "What transformation areas should FinNova consider based on the available evidence?"
#     }

#     response = client.post("/api/questions/1", json=payload)

#     assert response.status_code == 200

#     data = response.json()

#     assert "question" in data
#     assert "answer" in data
#     assert "evidence_ids" in data
#     assert "model_used" in data

#     assert isinstance(data["answer"], str)
#     assert len(data["answer"]) > 0
#     assert isinstance(data["evidence_ids"], list)


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_question_endpoint(monkeypatch):
    # Mock the LLM response for a reproducible CI test.
    monkeypatch.setattr(
        "app.ai.answer_generator.generate_text",
        lambda prompt: (
            "FinNova should evaluate fraud prevention "
            "and operational automation using the "
            "available supporting evidence."
        ),
    )

    payload = {
        "question": (
            "What transformation areas should FinNova "
            "consider based on the available evidence?"
        )
    }

    response = client.post(
        "/api/questions/1",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert "question" in data
    assert "answer" in data
    assert "evidence_ids" in data
    assert "model_used" in data

    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0
    assert isinstance(data["evidence_ids"], list)
