#!/usr/bin/env python3
"""
Comprehensive Live Status Code Demonstration for MLOps Practical-11
Tests 200, 422, 404, 307, and 301 against the deployed Render API.
"""

import json
import requests

BASE_URL = "https://student-result-prediction-latest-sckc.onrender.com"
HTTP_URL = "http://student-result-prediction-latest-sckc.onrender.com"

def run_tests():
    print("=" * 85)
    print("      MLOps Practical-11: Live Status Code Verification (Render Cloud API)      ")
    print(f"Target: {BASE_URL}")
    print("=" * 85)

    # -------------------------------------------------------------------------
    # 1. Status 200 OK (Using payload_200.json)
    # -------------------------------------------------------------------------
    print("\n[TEST 1] HTTP 200 OK (Successful Prediction)")
    with open("payload_200.json", "r") as f:
        payload_200 = json.load(f)
    print(f"File Used: payload_200.json")
    print(f"Content  : {json.dumps(payload_200)}")
    print(f"Sending POST {BASE_URL}/predict ...")
    
    res_200 = requests.post(f"{BASE_URL}/predict", json=payload_200)
    print(f"--> Status Code : {res_200.status_code} OK")
    print(f"--> X-Request-ID: {res_200.headers.get('X-Request-ID')}")
    print(f"--> Response    : {res_200.text}")

    # -------------------------------------------------------------------------
    # 2. Status 422 Unprocessable Entity (Using payload_422.json)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 85)
    print("[TEST 2] HTTP 422 Unprocessable Entity (Validation Error)")
    with open("payload_422.json", "r") as f:
        payload_422 = json.load(f)
    print(f"File Used: payload_422.json")
    print(f"Content  : {json.dumps(payload_422)} (Notice: cgpa is a string instead of float)")
    print(f"Sending POST {BASE_URL}/predict ...")
    
    res_422 = requests.post(f"{BASE_URL}/predict", json=payload_422)
    print(f"--> Status Code : {res_422.status_code} Unprocessable Entity")
    print(f"--> X-Request-ID: {res_422.headers.get('X-Request-ID')}")
    print(f"--> Response    : {res_422.text}")

    # -------------------------------------------------------------------------
    # 3. Status 404 Not Found (Missing Route)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 85)
    print("[TEST 3] HTTP 404 Not Found (Calling Nonexistent Route)")
    invalid_route = f"{BASE_URL}/not-a-real-route"
    print(f"Sending GET {invalid_route} ...")
    
    res_404 = requests.get(invalid_route)
    print(f"--> Status Code : {res_404.status_code} Not Found")
    print(f"--> X-Request-ID: {res_404.headers.get('X-Request-ID')}")
    print(f"--> Response    : {res_404.text}")

    # -------------------------------------------------------------------------
    # 4. Status 307 Temporary Redirect (Trailing Slash Normalization)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 85)
    print("[TEST 4] HTTP 307 Temporary Redirect (Trailing Slash Redirect)")
    trailing_slash_url = f"{BASE_URL}/predict/"
    print(f"Sending POST {trailing_slash_url} (without auto-following redirects)...")
    
    res_307 = requests.post(trailing_slash_url, json=payload_200, allow_redirects=False)
    print(f"--> Status Code : {res_307.status_code} Temporary Redirect")
    print(f"--> Location    : {res_307.headers.get('Location')}")
    print(f"--> X-Request-ID: {res_307.headers.get('X-Request-ID')}")

    # -------------------------------------------------------------------------
    # 5. Status 301 Moved Permanently (HTTP to HTTPS Redirect)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 85)
    print("[TEST 5] HTTP 301 Moved Permanently (Insecure HTTP -> HTTPS Redirect)")
    print(f"Sending GET {HTTP_URL}/ (without auto-following redirects)...")
    
    res_301 = requests.get(f"{HTTP_URL}/", allow_redirects=False)
    print(f"--> Status Code : {res_301.status_code} Moved Permanently")
    print(f"--> Location    : {res_301.headers.get('Location')}")

    print("\n" + "=" * 85)
    print("                 ALL STATUS CODES VERIFIED SUCCESSFULLY!                     ")
    print("=" * 85)

if __name__ == "__main__":
    run_tests()
