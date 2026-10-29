from pathlib import Path
import argparse
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIFT_DIR = PROJECT_ROOT / "drift"
REFERENCE = DRIFT_DIR / "reference_data.csv"
OUTPUT = DRIFT_DIR / "current_data.csv"
LABELED_OUTPUT = DRIFT_DIR / "current_labeled_data.csv"
HISTORICAL = PROJECT_ROOT / "placement_data.csv"

FEATURES = [
    "cgpa",
    "placement_exam_marks",
]
TARGET = "placed"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--mode",
    choices=["stable", "drift"],
    default="stable"
)
args = parser.parse_args()

rng = np.random.default_rng(42)
df = pd.read_csv(HISTORICAL)
# Remaining 200 rows as current stream
recent_pool = df.iloc[800:].copy().reset_index(drop=True)

if len(recent_pool) < 100:
    recent_pool = df.sample(n=100, replace=True, random_state=42).reset_index(drop=True)

current = recent_pool.copy()

if args.mode == "stable":
    # Small natural noise
    current["cgpa"] = (current["cgpa"] + rng.normal(0, 0.05, size=len(current))).round(2)
    current["placement_exam_marks"] = (current["placement_exam_marks"] + rng.normal(0, 0.5, size=len(current))).round(1)
elif args.mode == "drift":
    # Realistic distribution shift on placement dataset
    current["cgpa"] = (current["cgpa"] - 0.8 + rng.normal(0, 0.05, size=len(current))).round(2)
    current["placement_exam_marks"] = (current["placement_exam_marks"] - 12.0 + rng.normal(0, 1.0, size=len(current))).round(1)

# Bounds
current["cgpa"] = current["cgpa"].clip(0.0, 10.0)
current["placement_exam_marks"] = current["placement_exam_marks"].clip(0.0, 100.0)

# Unlabeled current stream
current[FEATURES].to_csv(OUTPUT, index=False)
print("Mode:", args.mode)
print("Rows:", len(current))
print("File:", OUTPUT)

# Labeled current stream for retraining
if args.mode == "drift":
    # Re-evaluate placement labels under drifted distribution
    # Students with lower CGPA and marks have lower chance of placement
    prob = 1 / (1 + np.exp(-(0.8 * (current["cgpa"] - 6.5) + 0.04 * (current["placement_exam_marks"] - 30))))
    current[TARGET] = (prob > 0.5).astype(int)

current[FEATURES + [TARGET]].to_csv(LABELED_OUTPUT, index=False)
print("Labeled recent batch created:", LABELED_OUTPUT)
