from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIFT_DIR = PROJECT_ROOT / "drift"
# Primary dataset: placement_data.csv (user's dataset)
SOURCE = PROJECT_ROOT / "placement_data.csv"
OUTPUT = DRIFT_DIR / "reference_data.csv"

FEATURES = [
    "cgpa",
    "placement_exam_marks",
]
TARGET = "placed"

df = pd.read_csv(SOURCE)
missing = [c for c in FEATURES if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

# Use first 800 rows as historical reference
reference = df[FEATURES + ([TARGET] if TARGET in df.columns else [])].iloc[:800].dropna().copy()
DRIFT_DIR.mkdir(parents=True, exist_ok=True)
reference.to_csv(OUTPUT, index=False)
print("Reference dataset created for placement_data.csv.")
print("Rows:", len(reference))
print("Features:", FEATURES)
print("File:", OUTPUT)
