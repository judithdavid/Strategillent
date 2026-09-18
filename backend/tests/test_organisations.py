
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_organisation():
    unique_name = f"Pytest Organisation {uuid.uuid4()}"

    payload = {
        "name": unique_name,
        "fictional": True,
        "industry": "Fintech",
        "business_model": ["Digital Payments"],
        "markets": ["India"],
        "customers": 1000,
        "employees": 50,
        "products": ["Payments"],
        "challenges": ["Testing challenge"],
    }

    response = client.post("/api/organisations", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == unique_name
    assert data["industry"] == "Fintech"