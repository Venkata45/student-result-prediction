# Student Result Prediction - MLOps Pipeline

This project builds, tests, containerizes, publishes to GitHub Container Registry (GHCR), and deploys a FastAPI machine learning service to Render.

## Dataset
Predicts student placement outcome (`placed`: 0 or 1) based on:
- `cgpa` (0.0 to 10.0)
- `placement_exam_marks` (0.0 to 100.0)

## API Endpoints
- `GET /`: Service status and version
- `GET /health`: Health check endpoint
- `GET /docs`: Interactive Swagger UI documentation
- `POST /predict`: Prediction endpoint

## Pipeline
1. **GitHub Actions**: Tests container health and publishes Docker image to GHCR (`ghcr.io/venkata45/student-result-prediction:latest`).
2. **Render**: Pulls the prebuilt image from GHCR and deploys as a public cloud Web Service.
