# ADR 0004: Local-Only Philosophy for Demo

Status: Accepted
Date: 2025-08-29

## Context

Reviewers need to clone, run, and explore quickly. Deployment, CI/CD, and production hardening can distract from the demo flow.

## Decision

- Keep the project intentionally local-only for the demo.
- Quarantine deployment/infra artifacts under `infra/` and avoid CI configuration.
- Provide polished docs and scripts to run locally.

## Rationale

- Focus time on DX and showcasing API/UI rather than maintaining incomplete infra.
- Reduces noise in the repository and speeds up onboarding.

## Consequences

- No production deployment guidance is provided in this phase.
- Some settings are permissive for local convenience (e.g., CORS).

## Alternatives Considered

- Adding Docker + CI end-to-end. Useful, but outside the scope and raises maintenance cost.

## References

- See `README.md` for quickstart and demo script.
