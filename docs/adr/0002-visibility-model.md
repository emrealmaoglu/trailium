# ADR 0002: Visibility Model and Deny Strategy

Status: Accepted
Date: 2025-08-29

## Context

Users and content require a simple privacy model suitable for demos but realistic enough to exercise policy checks in both API and UI.

## Decision

- Visibility levels: `public`, `followers`, `private`.
- On access denial, return 404 Not Found instead of 403 to avoid leaking existence.
- Centralize checks in a policy/helper layer used by viewsets.

## Rationale

- These three levels cover common social scenarios while staying easy to grasp during a demo.
- Returning 404 prevents enumeration and keeps responses consistent.
- Centralized policy avoids duplicating rules and ensures consistent behavior across endpoints.

## Consequences

- API consumers must handle 404 for visibility denials.
- UI should present friendly messaging and CTAs (e.g., follow) when items are not visible.

## Alternatives Considered

- Returning 403 with structured error codes. Clearer, but risks information leakage in demos.

## References

- Code policy helpers live under backend `users.policies` and related modules.
