"""
Production Test Traffic Generator for Render (Practical-11 Step 19)
URL: https://student-result-prediction-latest-sckc.onrender.com
"""
import requests
import json
import time

BASE_URL = "https://student-result-prediction-latest-sckc.onrender.com"

def generate_traffic():
    print(f"Targeting Render Service: {BASE_URL}\n")

    # 1. Root and Health check
    print("1. Sending GET / ...")
    r = requests.get(f"{BASE_URL}/")
    print(f"Status: {r.status_code} | Body: {r.text} | X-Request-ID: {r.headers.get('X-Request-ID')}\n")

    print("2. Sending GET /health ...")
    r = requests.get(f"{BASE_URL}/health")
    print(f"Status: {r.status_code} | Body: {r.text} | X-Request-ID: {r.headers.get('X-Request-ID')}\n")

    # 2. Valid predict
    print("3. Sending Valid POST /predict ...")
    valid_payload = {"cgpa": 7.19, "placement_exam_marks": 26.0}
    r = requests.post(f"{BASE_URL}/predict", json=valid_payload)
    print(f"Status: {r.status_code} | Body: {r.text} | X-Request-ID: {r.headers.get('X-Request-ID')}\n")

    # 3. Invalid predict (Validation failure -> 422)
    print("4. Sending Invalid POST /predict (Expect 422) ...")
    invalid_payload = {"cgpa": "not-a-number", "placement_exam_marks": 26.0}
    r = requests.post(f"{BASE_URL}/predict", json=invalid_payload)
    print(f"Status: {r.status_code} | Body: {r.text} | X-Request-ID: {r.headers.get('X-Request-ID')}\n")

    # 4. Missing route (Expect 404)
    print("5. Sending GET /not-a-real-route (Expect 404) ...")
    r = requests.get(f"{BASE_URL}/not-a-real-route")
    print(f"Status: {r.status_code} | Body: {r.text} | X-Request-ID: {r.headers.get('X-Request-ID')}\n")

    print("Done! Open your Render Dashboard -> Logs to inspect the corresponding log entries.")

if __name__ == "__main__":
    generate_traffic()
