# ADR 0003: i18n Approach for Frontend

Status: Accepted
Date: 2025-08-29

## Context

The UI must be switchable between Turkish and English to support local audiences and reviewers.

## Decision

- Use `vue-i18n` v9 for message localization.
- Default language: Turkish (TR). Optional: English (EN).
- Message keys are stable, English-like identifiers; translations live in language files.

## Rationale

- `vue-i18n` is the standard for Vue 3 and integrates well with composition API.
- TR-first default matches target audience while keeping EN available for reviewers.
- Stable keys decouple code from copy changes.

## Consequences

- All user-visible strings should use i18n keys.
- New features must add TR and EN messages at the same time.

## Alternatives Considered

- Hardcoded strings: fastest initially, but blocks language switching and testing.

## References

- Frontend implementation under `apps/frontend/src/i18n.ts` and message files.
