## Why

Briefly explain the problem or goal this PR addresses.

## How

Summarize the approach and key changes. Link to ADRs if applicable.

## Result

What should a reviewer observe? Any DX improvements?

## Testing Steps

1. Backend: venv → install → migrate → seed_demo → runserver
2. Frontend: install → dev
3. Manual checks (list exact flows)

## Screenshots / Recordings

Attach images or short videos for UI changes.

## Definition of Done

- [ ] Unit of work is atomic & reversible
- [ ] Local run works (backend + frontend)
- [ ] i18n keys added (TR/EN)
- [ ] States present (loading/empty/error)
- [ ] OpenAPI/README updated if endpoints/UX changed
- [ ] No deployment artifacts added
