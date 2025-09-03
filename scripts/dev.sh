#!/usr/bin/env bash
set -euo pipefail

# Load env if present
if [ -f .env.development ]; then
  export $(grep -v '^#' .env.development | xargs) || true
fi
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs) || true
fi

# Defaults
export VITE_API_BASE=${VITE_API_BASE:-http://localhost:8000}

# Start backend
(
  cd apps/backend
  source ../../.venv/bin/activate 2>/dev/null || true
  python manage.py runserver 8000
) &

# Start frontend
(
  cd apps/frontend
  VITE_API_BASE=$VITE_API_BASE npm run dev -- --host
) &

wait
