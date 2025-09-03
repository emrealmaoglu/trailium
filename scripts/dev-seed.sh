#!/usr/bin/env bash
set -euo pipefail

cd apps/backend
source ../../.venv/bin/activate 2>/dev/null || true

python manage.py migrate
# deterministic dev users + demo data
python manage.py create_dev_users || true
python manage.py create_demo_users --count 20 || true

echo "Seed completed."
