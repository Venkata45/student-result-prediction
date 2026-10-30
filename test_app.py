from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    assert "X-Request-ID" in res.headers

def test_metrics_endpoint():
    """Verify /metrics returns Prometheus text format and model_loaded gauge"""
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "student_api_model_loaded 1.0" in res.text
    assert "student_api_http_requests_total" in res.text
    assert "student_api_http_request_duration_seconds" in res.text
    assert "student_api_predictions_total" in res.text

def test_valid_predict():
    res = client.post("/predict", json={"cgpa": 7.19, "placement_exam_marks": 26.0})
    assert res.status_code == 200
    data = res.json()
    assert "placed" in data
    assert "X-Request-ID" in res.headers

    # Check that predictions counter incremented
    metrics_res = client.get("/metrics")
    assert 'student_api_predictions_total{result="success"}' in metrics_res.text

def test_invalid_predict_422():
    res = client.post("/predict", json={"cgpa": "not-a-number", "placement_exam_marks": 26.0})
    assert res.status_code == 422
    assert "X-Request-ID" in res.headers

    # Check that 422 is counted in http_requests_total
    metrics_res = client.get("/metrics")
    assert 'student_api_http_requests_total{method="POST",path="/predict",status="422"}' in metrics_res.text

def test_missing_route_404():
    res = client.get("/not-a-real-route")
    assert res.status_code == 404
    assert "X-Request-ID" in res.headers

def test_explicit_404_endpoint():
    res = client.get("/error/404")
    assert res.status_code == 404

def test_explicit_302_redirect_endpoint():
    res = client.get("/redirect/302", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["location"] == "/docs"
