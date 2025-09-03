#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT_DIR/apps/backend/.env"

if [ -f "$ENV_FILE" ]; then
  # shellcheck disable=SC2046
  export $(grep -E '^(POSTGRES_DB|POSTGRES_USER|POSTGRES_PASSWORD|POSTGRES_HOST|POSTGRES_PORT|PG_SUPERUSER|PG_SUPERPASSWORD)=' "$ENV_FILE" | xargs) || true
fi

echo "Running Django management command to bootstrap local Postgres..."
python "$ROOT_DIR/apps/backend/manage.py" bootstrap_db

echo "Next steps:"
echo "  cd apps/backend && python manage.py migrate"
