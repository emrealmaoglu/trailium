# Architecture (Stub)

- Backend: Django + DRF + SimpleJWT + PostgreSQL
- Frontend: Vue 3 + Vite + Pinia + Tailwind
- Monorepo: `apps/backend`, `apps/frontend`, `infra/compose`
- API base: `/api/*` with page-number pagination (`?page=&page_size=`)
- Auth: access/refresh, remember-me refresh lifetime, idle timeout.
