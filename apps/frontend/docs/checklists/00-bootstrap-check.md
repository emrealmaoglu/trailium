## Trailium Frontend — Bootstrap QA Report

### Environment
- Node: v24.6.0
- npm: 11.5.1

### 1) Project boots
- Command: `npm run dev -- --host`
- Output:
  - `VITE v7.1.3  ready in 233 ms`
- Status: PASS

### 2) File/Folder structure
- Required paths present:
  - apps/frontend/index.html — OK
  - apps/frontend/src/main.js — OK
  - apps/frontend/src/App.vue — OK
  - apps/frontend/src/layouts/AppShell.vue — OK
  - apps/frontend/src/router/index.js — OK
  - apps/frontend/src/pages/Home.vue — OK
  - apps/frontend/src/pages/Todos.vue — OK
  - apps/frontend/src/pages/Posts.vue — OK
  - apps/frontend/src/pages/Albums.vue — OK
  - apps/frontend/src/assets/brand/N2Mobil-Logotype.png — OK
  - apps/frontend/src/index.css — OK
  - apps/frontend/src/styles/theme.css — OK
- Status: PASS

### 3) index.html hygiene
- Single html/head/body document — OK
- Title contains “Trailium” — OK
- Poppins font links present — OK
- `<div id="app"></div>` and main entry present — OK
- Status: PASS

### 4) Styles wired up (Tailwind NOT installed yet)
- main.js imports `./index.css` and `./styles/theme.css` — OK
- No active `@tailwind` directives — FIXED (removed from src/index.css)
- Status: PASS

### 5) Router
- Uses `createRouter` + `createWebHistory` — OK
- Routes: '/', '/todos', '/posts', '/albums' — OK
- `<RouterView />` rendered in layout — OK
- Status: PASS

### 6) AppShell layout
- Sidebar + Topbar + Content with `<RouterView />` — OK
- Compact circular logo on left, “Trailium” aligned right — OK
- Status: PASS

### 7) App.vue cleanliness
- Single `<template>` rendering only `<AppShell />` — OK
- Status: PASS

### 8) Logo import paths
- Relative imports used where logo is referenced — OK
- Image uses `object-left object-cover` — OK
- Status: PASS

### 9) No oversized hero logo on home
- Home.vue is a simple heading + paragraph — OK
- Status: PASS

### 10) Theme notes (for later)
- Recorded color keys: brand.gray, brand.black, brand.grayLight, brand.gray2, brand.purple — OK
- Status: PASS

### 11) Git
- Changes made:
  - Edited: `src/index.css` (removed @tailwind directives)
  - Added: `docs/checklists/00-bootstrap-check.md` (this report)
- Commit message: `chore(frontend): bootstrap checks pass, fix imports/layout/styles wiring`

### Next Step
Users grid + user card components (hover rows, icon list, mock data).
