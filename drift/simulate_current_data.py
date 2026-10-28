from pathlib import Path
import argparse
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIFT_DIR = PROJECT_ROOT / "drift"
REFERENCE = DRIFT_DIR / "reference_data.csv"
OUTPUT = DRIFT_DIR / "current_data.csv"
LABELED_OUTPUT = DRIFT_DIR / "current_labeled_data.csv"
HISTORICAL = PROJECT_ROOT / "student_results.csv"

FEATURES = [
    "attendance",
    "internal_marks",
    "assignment_marks",
    "previous_score",
]

parser = argparse.ArgumentParser()
parser.add_argument(
    "--mode",
    choices=["stable", "drift"],
    default="stable"
)
args = parser.parse_args()

rng = np.random.default_rng(42)
reference = pd.read_csv(REFERENCE)
n = min(100, len(reference))
current = reference.sample(
    n=n,
    replace=True,
    random_state=42
).reset_index(drop=True)

# Small random noise for both modes
for feature in FEATURES:
    current[feature] = (
        current[feature]
        + rng.normal(0, 1.0, size=len(current))
    )

if args.mode == "drift":
    # Classroom-only synthetic shift
    current["attendance"] -= 15
    current["internal_marks"] -= 10
    current["assignment_marks"] -= 8
    current["previous_score"] -= 5

# Keep common mark/percentage features in a sensible range
for feature in FEATURES:
    current[feature] = current[feature].clip(0, 100)

current.to_csv(OUTPUT, index=False)
print("Mode:", args.mode)
print("Rows:", len(current))
print("File:", OUTPUT)

# When drift is simulated, also create the labeled recent batch needed for retraining
if args.mode == "drift":
    score = (
        0.05 * (current["attendance"] - 75) +
        0.12 * (current["internal_marks"] - 35) +
        0.10 * (current["assignment_marks"] - 35) +
        0.04 * (current["previous_score"] - 70) +
        rng.normal(0, 0.5, len(current))
    )
    prob = 1 / (1 + np.exp(-score))
    labeled = current.copy()
    labeled["result"] = ["PASS" if p > 0.5 else "FAIL" for p in prob]
    labeled.to_csv(LABELED_OUTPUT, index=False)
    print("Labeled recent batch created:", LABELED_OUTPUT)
