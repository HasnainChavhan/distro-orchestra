import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_analyze():
    response = client.post("/analyze", json={"text": "I love this!"})
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data
    assert data["sentiment"] in ["POSITIVE", "NEGATIVE", "NEUTRAL"]
    assert "confidence" in data
    assert "probabilities" in data

def test_analyze_batch():
    response = client.post("/analyze/batch", json={"texts": ["I love this!", "I hate this!"]})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["results"]) == 2
    assert data["results"][0]["sentiment"] in ["POSITIVE", "NEGATIVE", "NEUTRAL"]
