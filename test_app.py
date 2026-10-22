from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    assert "X-Request-ID" in res.headers

def test_valid_predict():
    res = client.post("/predict", json={"cgpa": 7.19, "placement_exam_marks": 26.0})
    assert res.status_code == 200
    data = res.json()
    assert "placed" in data
    assert "X-Request-ID" in res.headers

def test_invalid_predict_422():
    res = client.post("/predict", json={"cgpa": "not-a-number", "placement_exam_marks": 26.0})
    assert res.status_code == 422
    assert "X-Request-ID" in res.headers

def test_missing_route_404():
    res = client.get("/not-a-real-route")
    assert res.status_code == 404
    assert "X-Request-ID" in res.headers
