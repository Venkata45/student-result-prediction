
from fastapi import FastAPI
from pydantic import BaseModel, Field
import pandas as pd
from sklearn.linear_model import LogisticRegression

app = FastAPI(title="Student Result Prediction API")

# Load your dataset
data = pd.read_csv("placement_data.csv")

X = data[["cgpa", "placement_exam_marks"]]
y = data["placed"]

# Train the model
model = LogisticRegression(max_iter=1000)
model.fit(X, y)


class Student(BaseModel):
    cgpa: float = Field(ge=0, le=10)
    placement_exam_marks: float = Field(ge=0)


@app.get("/")
def root():
    return {
        "message": "Student Result Prediction API is running",
        "version": "1.0.1"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict")
def predict(student: Student):
    values = pd.DataFrame(
        [[student.cgpa, student.placement_exam_marks]],
        columns=["cgpa", "placement_exam_marks"]
    )

    result = int(model.predict(values)[0])
    probabilities = model.predict_proba(values)[0]
    placed_index = list(model.classes_).index(1)

    return {
        "placed": result,
        "result": "PLACED" if result == 1 else "NOT PLACED",
        "placement_probability": round(
            float(probabilities[placed_index]), 4
        )
    }

