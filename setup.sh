#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/apps/backend-fastapi"
BACKEND_VENV="$BACKEND_DIR/.venv"
FRONTEND_ENV_FILE="$ROOT_DIR/apps/web-antd/.env.development"
FRONTEND_PORT="${VITE_PORT:-5666}"
BACKEND_PORT="${APP_PORT:-8000}"

FRONTEND_PID=""
BACKEND_PID=""
PNPM_CMD=()

log() {
  printf '[setup] %s\n' "$1"
}

fail() {
  printf '[setup] %s\n' "$1" >&2
  exit 1
}

load_env_value() {
  local file="$1"
  local key="$2"

  if [[ -f "$file" ]]; then
    local value
    value="$(grep -E "^${key}=" "$file" | tail -n 1 | cut -d '=' -f 2- || true)"
    value="${value%\"}"
    value="${value#\"}"
    printf '%s' "$value"
  fi
}

require_command() {
  local cmd="$1"
  local hint="${2:-}"

  if ! command -v "$cmd" >/dev/null 2>&1; then
    if [[ -n "$hint" ]]; then
      printf 'Missing required command: %s (%s)\n' "$cmd" "$hint" >&2
    else
      printf 'Missing required command: %s\n' "$cmd" >&2
    fi
    exit 1
  fi
}

port_in_use() {
  local port="$1"
  [[ -n "$(port_pids "$port")" ]]
}

print_port_owner() {
  local port="$1"
  lsof -nP -iTCP:"$port" -sTCP:LISTEN 2>/dev/null || true
}

port_pids() {
  local port="$1"
  lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null | sort -u || true
}

release_port() {
  local port="$1"
  local service_name="$2"
  local pids

  pids="$(port_pids "$port")"
  if [[ -z "$pids" ]]; then
    return 0
  fi

  log "$service_name port $port is in use, stopping existing process(es)"
  print_port_owner "$port"

  while read -r pid; do
    [[ -z "$pid" ]] && continue
    kill "$pid" >/dev/null 2>&1 || true
  done <<<"$pids"

  sleep 1

  if port_in_use "$port"; then
    log "$service_name port $port is still occupied, force killing remaining process(es)"
    pids="$(port_pids "$port")"
    while read -r pid; do
      [[ -z "$pid" ]] && continue
      kill -9 "$pid" >/dev/null 2>&1 || true
    done <<<"$pids"
    sleep 1
  fi

  if port_in_use "$port"; then
    print_port_owner "$port"
    fail "Unable to free $service_name port $port."
  fi
}

cleanup() {
  local exit_code=$?

  if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
    log "Stopping backend (PID: $BACKEND_PID)"
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi

  if [[ -n "$FRONTEND_PID" ]] && kill -0 "$FRONTEND_PID" >/dev/null 2>&1; then
    log "Stopping frontend (PID: $FRONTEND_PID)"
    kill "$FRONTEND_PID" >/dev/null 2>&1 || true
  fi

  exit "$exit_code"
}

trap cleanup EXIT INT TERM

if command -v pnpm >/dev/null 2>&1; then
  PNPM_CMD=(pnpm)
elif command -v corepack >/dev/null 2>&1; then
  PNPM_CMD=(corepack pnpm)
else
  fail "Missing required command: pnpm or corepack (install pnpm >= 10)"
fi
require_command python3 "install Python 3.12+"
require_command docker "install Docker"
require_command lsof "install lsof"

if docker compose version >/dev/null 2>&1; then
  DOCKER_COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  DOCKER_COMPOSE=(docker-compose)
else
  printf 'Missing docker compose support. Install Docker Compose.\n' >&2
  exit 1
fi

frontend_port_from_file="$(load_env_value "$FRONTEND_ENV_FILE" "VITE_PORT")"
if [[ -n "$frontend_port_from_file" ]]; then
  FRONTEND_PORT="$frontend_port_from_file"
fi

backend_port_from_file="$(load_env_value "$BACKEND_DIR/.env" "APP_PORT")"
if [[ -n "$backend_port_from_file" ]]; then
  BACKEND_PORT="$backend_port_from_file"
fi

release_port "$BACKEND_PORT" "Backend"
release_port "$FRONTEND_PORT" "Frontend"

log "Installing frontend dependencies"
cd "$ROOT_DIR"
"${PNPM_CMD[@]}" install

log "Starting PostgreSQL with Docker Compose"
"${DOCKER_COMPOSE[@]}" up -d postgres

if [[ ! -d "$BACKEND_VENV" ]]; then
  log "Creating backend virtual environment"
  python3 -m venv "$BACKEND_VENV"
fi

log "Installing backend dependencies"
"$BACKEND_VENV/bin/pip" install -e "$BACKEND_DIR[dev]"

if [[ ! -f "$BACKEND_DIR/.env" ]] && [[ -f "$BACKEND_DIR/.env.example" ]]; then
  log "Creating backend .env from .env.example"
  cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
fi

log "Running backend database migrations"
(
  cd "$BACKEND_DIR"
  "$BACKEND_VENV/bin/alembic" -c alembic.ini upgrade head
)

log "Starting backend on http://127.0.0.1:$BACKEND_PORT"
(
  cd "$BACKEND_DIR"
  "$BACKEND_VENV/bin/uvicorn" app.main:app --reload --host 0.0.0.0 --port "$BACKEND_PORT"
) &
BACKEND_PID=$!

log "Starting frontend"
(
  cd "$ROOT_DIR"
  "${PNPM_CMD[@]}" dev:antd -- --host 0.0.0.0 --port "$FRONTEND_PORT" --strictPort
) &
FRONTEND_PID=$!

log "Project is starting up"
log "Frontend URL: http://127.0.0.1:$FRONTEND_PORT"
log "Backend URL: http://127.0.0.1:$BACKEND_PORT"
log "Backend docs: http://127.0.0.1:$BACKEND_PORT/docs"
log "Press Ctrl+C to stop frontend and backend"

wait "$FRONTEND_PID" "$BACKEND_PID"
