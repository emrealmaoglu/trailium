# 0001 - Record architecture decisions

Date: 2025-01-01

## Status
Accepted

## Context
We manage backend and frontend in a single monorepo for consistency and velocity.

## Decision
Use Django + DRF + SimpleJWT + PostgreSQL for backend; Vue 3 + Vite + Pinia + Tailwind for frontend. Docker dev via compose.

## Consequences
Single CI pipeline, shared versioning, simpler onboarding, consistent lint/build tooling.
