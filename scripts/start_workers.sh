#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
RUNTIME_DIR="$ROOT_DIR/.runtime"
CELERY_PID_FILE="$RUNTIME_DIR/celery.pid"
API_PID_FILE="$RUNTIME_DIR/api.pid"
CELERY_LOG="$RUNTIME_DIR/celery.log"
API_LOG="$RUNTIME_DIR/api.log"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Missing virtual environment python at $PYTHON_BIN"
  echo "Create and install dependencies first:"
  echo "  python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

mkdir -p "$RUNTIME_DIR"

echo "[1/5] Starting infrastructure (PostgreSQL + Redis)..."
docker compose up -d

echo "[2/5] Applying database migrations..."
"$PYTHON_BIN" -m alembic upgrade head

echo "[3/5] Releasing port conflicts from old API container (if present)..."
docker rm -f ai-service-platform-api >/dev/null 2>&1 || true

stop_if_running() {
  local pid_file="$1"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file")"
    if [[ -n "$pid" ]] && kill -0 "$pid" >/dev/null 2>&1; then
      kill "$pid" >/dev/null 2>&1 || true
      sleep 1
    fi
    rm -f "$pid_file"
  fi
}

stop_if_running "$CELERY_PID_FILE"
stop_if_running "$API_PID_FILE"

echo "[4/5] Starting Celery worker..."
PYTHONPATH=. nohup "$PYTHON_BIN" -m celery -A app.workers.celery_app:celery_app worker \
  -Q default,ai_tasks,events,webhooks --loglevel=info > "$CELERY_LOG" 2>&1 &
echo $! > "$CELERY_PID_FILE"

echo "[5/5] Starting FastAPI API..."
PYTHONPATH=. nohup "$PYTHON_BIN" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$API_LOG" 2>&1 &
echo $! > "$API_PID_FILE"

sleep 3

if curl -sS --max-time 5 http://localhost:8000/ | grep -q 'API running'; then
  echo ""
  echo "Startup completed successfully."
  echo "- API PID: $(cat "$API_PID_FILE")"
  echo "- Celery PID: $(cat "$CELERY_PID_FILE")"
  echo "- API log: $API_LOG"
  echo "- Celery log: $CELERY_LOG"
else
  echo ""
  echo "Startup completed but API health check failed."
  echo "Check logs:"
  echo "- $API_LOG"
  echo "- $CELERY_LOG"
  exit 1
fi
