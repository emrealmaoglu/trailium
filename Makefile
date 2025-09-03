SHELL := /bin/bash

.PHONY: dev dev-seed migrate seed backend frontend

venv := .venv

migrate:
	cd apps/backend && source ../../$(venv)/bin/activate && python manage.py migrate

seed:
	bash scripts/dev-seed.sh

backend:
	cd apps/backend && source ../../$(venv)/bin/activate && python manage.py runserver 8000

frontend:
	cd apps/frontend && VITE_API_BASE=$${VITE_API_BASE:-http://localhost:8000} npm run dev -- --host

dev:
	bash scripts/dev.sh

dev-seed:
	bash scripts/dev-seed.sh
