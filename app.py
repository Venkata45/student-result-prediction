import logging
import sys
import time
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response, RedirectResponse
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
import pandas as pd
from pydantic import BaseModel, Field
from sklearn.linear_model import LogisticRegression

# Step 4 - Prometheus imports
from prometheus_client import Counter, Histogram, Gauge
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Step 4 (Practical-11) - Logger Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger("student-result-api")

# Step 5 - Define Application Metrics (Prometheus)
HTTP_REQUESTS = Counter(
    "student_api_http_requests_total",
    "Total HTTP requests received by the Student Result Prediction API",
    ["method", "path", "status"],
)
HTTP_LATENCY = Histogram(
    "student_api_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)
PREDICTIONS = Counter(
    "student_api_predictions_total",
    "Total Student Result Prediction attempts",
    ["result"],
)
MODEL_LOADED = Gauge(
    "student_api_model_loaded",
    "Whether the Student Result Prediction model is loaded",
)

# Step 6 - Connect Model-Loaded Gauge
DATA_FILE = "placement_data.csv"
try:
    data = pd.read_csv(DATA_FILE)
    X = data[["cgpa", "placement_exam_marks"]]
    y = data["placed"]
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    MODEL_LOADED.set(1)
    logger.info("event=model_loaded model_file=%s", DATA_FILE)
except Exception:
    MODEL_LOADED.set(0)
    logger.exception("event=model_load_failed model_file=%s", DATA_FILE)
    raise

# FastAPI application instance
app = FastAPI(
    title="Student Result Prediction API",
    description="MLOps Practical-12: Prometheus Metrics and Monitoring API",
    version="1.2.0",
)

# Step 7 - Extend Request/Response Middleware with Prometheus Metrics
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    path = request.url.path
    method = request.method
    start = time.perf_counter()
    try:
        response = await call_next(request)
        duration = time.perf_counter() - start
        duration_ms = duration * 1000

        # Do not count Prometheus' own scrape requests in user-traffic metrics
        if path != "/metrics":
            HTTP_REQUESTS.labels(
                method=method,
                path=path,
                status=str(response.status_code),
            ).inc()
            HTTP_LATENCY.labels(
                method=method,
                path=path,
            ).observe(duration)

        level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(
            level,
            "event=http_request request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception:
        duration = time.perf_counter() - start
        duration_ms = duration * 1000

        if path != "/metrics":
            HTTP_REQUESTS.labels(
                method=method,
                path=path,
                status="500",
            ).inc()
            HTTP_LATENCY.labels(
                method=method,
                path=path,
            ).observe(duration)

        logger.exception(
            "event=http_request_failed request_id=%s method=%s path=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

# Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    fields = [
        ".".join(str(part) for part in error.get("loc", []))
        for error in exc.errors()
    ]
    logger.warning(
        "event=validation_error path=%s field_locations=%s error_count=%s",
        request.url.path,
        fields,
        len(exc.errors()),
    )
    return await request_validation_exception_handler(request, exc)

# Student Result Schema
class Student(BaseModel):
    cgpa: float = Field(ge=0, le=10, description="Cumulative Grade Point Average (0 to 10)")
    placement_exam_marks: float = Field(ge=0, description="Placement exam marks")

    model_config = {
        "json_schema_extra": {
            "example": {
                "cgpa": 7.19,
                "placement_exam_marks": 26.0,
            }
        }
    }

SAFE_INPUT_FIELDS = {"cgpa", "placement_exam_marks"}

# Endpoints
@app.get("/")
def root():
    return {
        "message": "Student Result Prediction API is running",
        "version": "1.2.0",
        "practical": "Practical-12: Monitoring with Prometheus and Grafana",
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
    }

# Step 9 - Add the /metrics Endpoint
@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )

# Step 8 - Count Prediction Successes and Runtime Failures
@app.post("/predict")
def predict(student: Student):
    try:
        payload = student.model_dump()
        safe_input = {
            key: value
            for key, value in payload.items()
            if key in SAFE_INPUT_FIELDS
        }
        logger.info(
            "event=prediction_request feature_names=%s safe_input=%s",
            sorted(payload.keys()),
            safe_input,
        )

        values = pd.DataFrame(
            [[student.cgpa, student.placement_exam_marks]],
            columns=["cgpa", "placement_exam_marks"],
        )

        result = int(model.predict(values)[0])
        probabilities = model.predict_proba(values)[0]
        placed_index = list(model.classes_).index(1)

        # Increment Prometheus success counter
        PREDICTIONS.labels(result="success").inc()
        logger.info(
            "event=prediction_success prediction=%s",
            str(result),
        )

        return {
            "placed": result,
            "prediction": str(result),
            "result": "PLACED" if result == 1 else "NOT PLACED",
            "placement_probability": round(
                float(probabilities[placed_index]), 4
            ),
        }
    except Exception:
        # Increment Prometheus error counter
        PREDICTIONS.labels(result="error").inc()
        logger.exception("event=prediction_failed")
        raise HTTPException(status_code=500, detail="Prediction failed")

# Demonstration Endpoints for Swagger UI (404 and 302)
@app.get("/error/404", summary="Simulate 404 Not Found Error", tags=["Status Code Demonstrations"])
def simulate_404():
    """Explicitly triggers an HTTP 404 Not Found error inside FastAPI."""
    raise HTTPException(status_code=404, detail="Resource not found (Simulated 404 for Lab Demonstration)")

@app.get("/redirect/302", summary="Simulate 302 Redirection", tags=["Status Code Demonstrations"])
def simulate_302():
    """Explicitly triggers an HTTP 302 Found redirect to /docs."""
    return RedirectResponse(url="/docs", status_code=302)
