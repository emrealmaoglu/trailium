# API Contract

- Base URL: `/api/`
- Pagination: Page number with `?page=N&page_size=M`.
- Auth: JWT access/refresh; refresh lifetime depends on remember-me; idle timeout on frontend.
- OpenAPI schema: generated via `python manage.py spectacular --file openapi.json` (see repo root `openapi.json`).
- Postman: import `postman_collection.json` in the repo root.
