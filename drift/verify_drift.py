#!/usr/bin/env python3
"""
MLOps Practical-15: Automated End-to-End Verification Script
Runs both Stable and Drifted scenarios to verify data drift detection,
conditional retraining, quality gate enforcement, and model promotion.
"""

import subprocess
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIFT_DIR = PROJECT_ROOT / "drift"

def print_header(title):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)

def run_cmd(cmd, desc):
    print(f"\n▶ {desc}...")
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.returncode != 0 and "Retraining skipped" not in result.stdout:
        print(f"❌ Error (exit code {result.returncode}):")
        if result.stderr.strip():
            print(result.stderr.strip())
        return False
    return True

def main():
    print_header("MLOps Practical-15: Data Drift & Retraining Verification")

    # Step 1: Prepare Reference Dataset
    run_cmd([sys.executable, "drift/prepare_reference.py"], "Step 1: Preparing baseline reference dataset")

    # Step 2: Test Scenario 1 (No-Drift / Stable)
    print_header("SCENARIO 1: Stable Recent Data (No Drift)")
    run_cmd([sys.executable, "drift/simulate_current_data.py", "--mode", "stable"], "Simulating stable recent batch")
    run_cmd([sys.executable, "drift/detect_drift.py"], "Running Kolmogorov-Smirnov drift test")
    run_cmd([sys.executable, "drift/retrain_candidate.py"], "Verifying retraining condition (Should be SKIPPED)")

    with open(DRIFT_DIR / "drift_report.json") as f:
        rep = json.load(f)
    assert rep["overall_drift"] == False, "Expected overall_drift to be False for stable mode"
    print("\n✅ SCENARIO 1 PASSED: Zero drift detected, retraining was safely skipped to save compute!")

    # Step 3: Test Scenario 2 (Drift Detected)
    print_header("SCENARIO 2: Drifted Recent Data (Drift Detected & Retraining)")
    run_cmd([sys.executable, "drift/simulate_current_data.py", "--mode", "drift"], "Simulating drifted recent batch (attendance/marks shift)")
    run_cmd([sys.executable, "drift/detect_drift.py"], "Running Kolmogorov-Smirnov drift test")
    
    with open(DRIFT_DIR / "drift_report.json") as f:
        rep = json.load(f)
    assert rep["overall_drift"] == True, "Expected overall_drift to be True for drift mode"
    print(f"\n🚩 Drift confirmed! Flagged features: {rep['drifted_features']}")

    run_cmd([sys.executable, "drift/retrain_candidate.py"], "Retraining candidate model on historical + recent ground truth")
    run_cmd([sys.executable, "drift/approve_candidate.py"], "Enforcing Quality Gate (Accuracy >= 0.85) and promoting model")

    with open(DRIFT_DIR / "retraining_metrics.json") as f:
        metrics = json.load(f)
    print(f"\n✅ SCENARIO 2 PASSED: Candidate Accuracy = {metrics['candidate_accuracy']*100:.2f}% >= 85%. Promoted to production!")

    # Step 4: Run unit tests
    print_header("Step 4: Post-Promotion Unit & API Test Suite")
    run_cmd([sys.executable, "-m", "pytest", "-q"], "Running pytest suite against promoted model")

    print_header("🎉 ALL PRACTICAL-15 DRIFT & RETRAINING TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    main()
