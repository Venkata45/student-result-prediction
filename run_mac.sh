#!/usr/bin/env bash
# ==============================================================================
# MLOps Practical - 12: One-Click Runner for macOS (MacBook)
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "================================================================================"
echo "      MLOps Practical - 12: Monitoring with Prometheus & Grafana (macOS)        "
echo "================================================================================"
echo "Project Path: $DIR"
echo ""

show_menu() {
    echo "Choose an action:"
    echo "  1) Run Tests (pytest test_app.py)"
    echo "  2) Run Practical-12 Metrics Verification (verify_metrics.py)"
    echo "  3) Start Local FastAPI Server (uvicorn app:app --reload)"
    echo "  4) Start Local Prometheus & Grafana Monitoring Stack (docker compose)"
    echo "  5) Stop Local Monitoring Stack (docker compose down)"
    echo "  6) Generate Test Traffic against live Render API"
    echo "  7) Push to GitHub (practical-12-monitoring and main)"
    echo "  8) Exit"
    echo ""
}

case "$1" in
    1|test)
        echo "[INFO] Running pytest test suite..."
        python3 -m pytest test_app.py -v -s
        ;;
    2|metrics)
        echo "[INFO] Running Prometheus metrics verification..."
        python3 Practical_12_Monitoring/verify_metrics.py
        ;;
    3|serve)
        echo "[INFO] Starting FastAPI server on http://127.0.0.1:8000 ..."
        echo "[INFO] Metrics exposed at http://127.0.0.1:8000/metrics"
        echo "[INFO] Swagger docs at http://127.0.0.1:8000/docs"
        python3 -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
        ;;
    4|monitor-up)
        echo "[INFO] Starting Prometheus and Grafana via Docker Compose..."
        cd Practical_12_Monitoring
        docker compose up -d
        echo "[SUCCESS] Prometheus running at: http://localhost:9090"
        echo "[SUCCESS] Grafana running at: http://localhost:3000"
        ;;
    5|monitor-down)
        echo "[INFO] Stopping monitoring stack..."
        cd Practical_12_Monitoring
        docker compose down
        ;;
    6|traffic)
        echo "[INFO] Generating test traffic against live Render service..."
        python3 test_all_status_codes.py
        ;;
    7|push)
        git add app.py requirements.txt test_app.py .github/workflows/docker-publish.yml Practical_12_Monitoring
        git commit -m "Update Practical 12 monitoring changes" || true
        git push -u origin practical-12-monitoring
        git checkout main
        git merge practical-12-monitoring
        git push origin main
        git checkout practical-12-monitoring
        echo "[SUCCESS] Pushed practical-12-monitoring and main to GitHub!"
        ;;
    *)
        show_menu
        read -p "Enter selection [1-8]: " choice
        case "$choice" in
            1) python3 -m pytest test_app.py -v -s ;;
            2) python3 Practical_12_Monitoring/verify_metrics.py ;;
            3) python3 -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload ;;
            4) cd Practical_12_Monitoring && docker compose up -d ;;
            5) cd Practical_12_Monitoring && docker compose down ;;
            6) python3 test_all_status_codes.py ;;
            7) 
                git add app.py requirements.txt test_app.py .github/workflows/docker-publish.yml Practical_12_Monitoring
                git commit -m "Update Practical 12 monitoring changes" || true
                git push -u origin practical-12-monitoring
                git checkout main
                git merge practical-12-monitoring
                git push origin main
                git checkout practical-12-monitoring
                ;;
            8) exit 0 ;;
            *) echo "Invalid option"; exit 1 ;;
        esac
        ;;
esac
