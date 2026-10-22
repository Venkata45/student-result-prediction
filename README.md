# Student Result Prediction — MLOps Cloud Deployment

[![GitHub Actions CI](https://github.com/Venkata45/student-result-prediction/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/Venkata45/student-result-prediction/actions)
[![GHCR Package](https://img.shields.io/badge/GHCR-Docker%20Image-blue?logo=docker)](https://github.com/users/Venkata45/packages/container/package/student-result-prediction)
[![Render Deployment](https://img.shields.io/badge/Render-Live%20API-46e3b7?logo=render&logoColor=black)](https://student-result-prediction-latest-sckc.onrender.com)
[![Swagger UI](https://img.shields.io/badge/API-Swagger%20Docs-009688?logo=fastapi&logoColor=white)](https://student-result-prediction-latest-sckc.onrender.com/docs)

This repository demonstrates the end-to-end MLOps deployment pipeline for the **Student Result Prediction** system, continuing from automated CI health validation to cloud web service hosting on Render.

---

## 🌐 Live Cloud Deployment Links

You can access and test the deployed cloud service directly from GitHub using the links below:

- 🚀 **Live Service URL:** [https://student-result-prediction-latest-sckc.onrender.com/](https://student-result-prediction-latest-sckc.onrender.com/)
- 📑 **Interactive Swagger UI (API Docs):** [https://student-result-prediction-latest-sckc.onrender.com/docs](https://student-result-prediction-latest-sckc.onrender.com/docs)
- 🩺 **Health Check Endpoint:** [https://student-result-prediction-latest-sckc.onrender.com/health](https://student-result-prediction-latest-sckc.onrender.com/health)
- 📦 **GHCR Container Package:** [ghcr.io/venkata45/student-result-prediction:latest](https://github.com/users/Venkata45/packages/container/package/student-result-prediction)

---

## 🧠 Dataset & Features
The model predicts whether a student gets placed (`placed`: `0` or `1`) based on:
1. `cgpa`: Cumulative Grade Point Average (0.0 to 10.0)
2. `placement_exam_marks`: Placement exam score (0.0 to 100.0)

---

## 📡 API Endpoints

| Method | Endpoint | Description | Sample Output |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Service status and version | `{"message":"Student Result Prediction API is running","version":"1.0.1"}` |
| `GET` | `/health` | Cloud liveness & readiness probe | `{"status":"healthy"}` |
| `GET` | `/docs` | Interactive Swagger UI API documentation | *Interactive web UI* |
| `POST` | `/predict` | Model inference prediction | `{"placed": 0, "result": "NOT PLACED", "placement_probability": 0.4979}` |

---

## 🧪 Testing with cURL

```bash
# 1. Health check
curl -s https://student-result-prediction-latest-sckc.onrender.com/health

# 2. Test prediction
curl -X POST "https://student-result-prediction-latest-sckc.onrender.com/predict" \
  -H "Content-Type: application/json" \
  -d '{"cgpa": 7.19, "placement_exam_marks": 26.0}'
```

---

## 🏗️ Architecture Pipeline

```text
Source Code (GitHub)
       ↓
GitHub Actions CI (Build & Container Health Test)
       ↓
GitHub Container Registry (GHCR)
       ↓ image pull
Render Cloud Web Service (Existing Image)
       ↓
Public HTTPS Endpoint (Swagger UI & REST API)
```
