# ADR 0001: Database and Authentication Choices

Status: Accepted
Date: 2025-08-29

## Context

The application is a local/demo social platform intended for reviewers to run quickly. We need a credible stack that matches real-world usage while avoiding production complexity.

## Decision

- Use PostgreSQL as the only supported database for local/demo.
- Use Django REST Framework for the API.
- Use Simple JWT for stateless authentication with short-lived access tokens and longer-lived refresh tokens.

## Rationale

- PostgreSQL provides realistic behavior (constraints, JSON fields, performant queries) that SQLite does not. This reduces “works locally but not in prod” surprises.
- DRF offers batteries-included API tooling we already use across the codebase (serializers, viewsets, permissions).
- Simple JWT is widely used, integrates natively with DRF, and matches our frontend needs.

## Details

- No SQLite fallback; local reviewers must have a running PostgreSQL instance.
- Token lifetimes for local demo: access 30 minutes; refresh 7 days. Rotation and blacklist are enabled to demo best practices without extra complexity.
- Authentication header type: `Authorization: Bearer <token>`.

## Consequences

- Slightly higher local setup cost (PostgreSQL) in exchange for realistic behavior.
- Sessions/cookies are not relied upon for auth; all API calls expect Bearer tokens.

## Alternatives Considered

- SQLite: faster to start but diverges from intended production-like behavior.
- Session auth: simpler but mismatched with SPA frontend and less portable to mobile.

## References

- DRF: https://www.django-rest-framework.org/
- SimpleJWT: https://django-rest-framework-simplejwt.readthedocs.io/
