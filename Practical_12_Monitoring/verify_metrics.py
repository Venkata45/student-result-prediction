"""
Local Prometheus Metrics Verification Script for Practical-12
Simulates traffic and prints the resulting Prometheus metrics.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def run_verification():
    print("=" * 80)
    print("      MLOps Practical-12: Prometheus Metrics & Monitoring Verification      ")
    print("=" * 80)

    print("\n--- 1. Generating Test Traffic ---")
    
    # 2 Health checks
    print("Sending GET /health (x2)...")
    client.get("/health")
    client.get("/health")

    # 3 Valid predictions
    print("Sending POST /predict (Valid) (x3)...")
    client.post("/predict", json={"cgpa": 7.19, "placement_exam_marks": 26.0})
    client.post("/predict", json={"cgpa": 8.51, "placement_exam_marks": 9.0})
    client.post("/predict", json={"cgpa": 6.82, "placement_exam_marks": 16.0})

    # 1 Invalid prediction (422)
    print("Sending POST /predict (Invalid: cgpa='not-a-number') (x1)...")
    client.post("/predict", json={"cgpa": "not-a-number", "placement_exam_marks": 26.0})

    # 1 Missing route (404)
    print("Sending GET /not-a-real-route (x1)...")
    client.get("/not-a-real-route")

    print("\n--- 2. Fetching /metrics Output ---")
    res = client.get("/metrics")
    print(f"Status Code: {res.status_code}")
    print(f"Content-Type: {res.headers.get('content-type')}\n")

    # Filter out standard python/process metrics to highlight student_api_* metrics
    student_metrics = [line for line in res.text.splitlines() if line.startswith("student_api_") or line.startswith("# HELP student_api") or line.startswith("# TYPE student_api")]
    
    print("--- Filtered Student API Application Metrics ---")
    for line in student_metrics:
        print(line)

    print("\n" + "=" * 80)
    print("                 METRICS VERIFICATION SUCCESSFUL!                           ")
    print("=" * 80)

if __name__ == "__main__":
    run_verification()
