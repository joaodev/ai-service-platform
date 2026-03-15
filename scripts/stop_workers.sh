#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

RUNTIME_DIR="$ROOT_DIR/.runtime"
CELERY_PID_FILE="$RUNTIME_DIR/celery.pid"
API_PID_FILE="$RUNTIME_DIR/api.pid"

stop_process() {
  local name="$1"
  local pid_file="$2"

  if [[ ! -f "$pid_file" ]]; then
    echo "- $name: PID file not found ($pid_file)"
    return
  fi

  local pid
  pid="$(cat "$pid_file")"

  if [[ -z "$pid" ]]; then
    echo "- $name: empty PID file"
    rm -f "$pid_file"
    return
  fi

  if kill -0 "$pid" >/dev/null 2>&1; then
    kill "$pid" >/dev/null 2>&1 || true
    sleep 1
    if kill -0 "$pid" >/dev/null 2>&1; then
      kill -9 "$pid" >/dev/null 2>&1 || true
    fi
    echo "- $name stopped (pid $pid)"
  else
    echo "- $name already stopped (pid $pid not running)"
  fi

  rm -f "$pid_file"
}

echo "Stopping local worker stack..."
stop_process "Celery worker" "$CELERY_PID_FILE"
stop_process "API server" "$API_PID_FILE"

echo "Done."
