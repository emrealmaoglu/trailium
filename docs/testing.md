# Trailium Regression Test Checklist (Frontend)

## Pre-flight
- Backend running at http://127.0.0.1:8000 (see test.sh)
- Frontend running at http://localhost:5173/
- .env in apps/frontend has VITE_API_BASE_URL=http://127.0.0.1:8000
- For favicon refresh: Clear storage + Shift-Reload

## Routes
- Open / (redirects /users) → Users grid page
- Open /users/:id/todos → Todos page for user
- Posts and Albums links present (placeholders OK)

## Branding
- Sidebar bottom-left: full N2Mobil logotype (icon + text), responsive, not cropped
- Header: ONLY “Trailium” text (no icon)
- Browser tab favicon: round symbol icon (public/favicon.png)

## Users Page
- Backend down → shows error state
- Backend up, no users → shows empty state
- With users: grid renders, skeleton visible on first load

## Todos Page
- List selector present
- Items show strike-through when done
- Toggling subitems updates item and list progress (bar + %)
- Loading, empty and error states render as expected

## Env-driven base URL
- Change VITE_API_BASE_URL to dummy → Users page errors
- Revert → recovers after reload
