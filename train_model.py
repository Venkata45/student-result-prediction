from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_FILE = PROJECT_ROOT / "student_results.csv"
MODEL_FILE = PROJECT_ROOT / "student_result_model.pkl"
METRICS_FILE = PROJECT_ROOT / "metrics.json"

FEATURES = [
    "attendance",
    "internal_marks",
    "assignment_marks",
    "previous_score",
]
TARGET = "result"

def train():
    df = pd.read_csv(DATA_FILE)
    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    preprocess = ColumnTransformer([
        ("numeric", numeric_pipeline, FEATURES),
    ])
    pipeline = Pipeline([
        ("preprocess", preprocess),
        ("model", LogisticRegression(max_iter=1000, random_state=42)),
    ])

    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, preds)

    metrics = {
        "accuracy": round(float(accuracy), 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
    }

    joblib.dump(pipeline, MODEL_FILE)
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Model trained successfully. Accuracy: {accuracy:.4f}")
    print(f"Model saved to: {MODEL_FILE}")

if __name__ == "__main__":
    train()
