# Trailium 



### Pre-commit Guard
- **Automatic blocking**: Git pre-commit hook prevents adding deployment/infra files
- **Installation**: `.git/hooks/pre-commit` is created automatically (requires `chmod +x`)
- **Bypass** (discouraged): `git commit --no-verify` for hook maintenance only
- **Blocked patterns**: Dockerfile, docker-compose, k8s/, terraform/, .github/workflows/, etc.

### Scope
- ✅ Local development, demo scenarios, UI/UX improvements


## Quickstart (3 minutes)
1. Clone: `git clone https://github.com/emrealmaoglu/trailium.git && cd trailium`
2. Env: `cp .env.example .env.development`
3. Seed (first run): `bash scripts/dev-seed.sh`
4. Run: `bash scripts/dev.sh`
   - Backend: http://localhost:8000
   - Frontend: http://localhost:5173

## Demo Scenario
- Login (dev user): emreaslan663 / demo123
- Users: follow 2–3 kişi
- Feed: beğen, yorum yap
- Posts: post ekle/düzenle, fotoğraflara tıkla (büyüt)

## Demo Data / Seeding
- Default demo users: 25 users with realistic Turkish data
- Premium rate: 15% (configurable via `DEMO_PREMIUM_RATE`)
- Private rate: 10% (configurable via `DEMO_PRIVATE_RATE`)
- To bias demo users (more premium/private), set `DEMO_PREMIUM_RATE` / `DEMO_PRIVATE_RATE` before running `dev-seed`
- Example: `DEMO_PREMIUM_RATE=0.30 DEMO_PRIVATE_RATE=0.20 bash scripts/dev-seed.sh`

## Environment
- Frontend base URL: `VITE_API_BASE` (default `http://localhost:8000`)
- Django debug true, SQLite varsayılan

### API Base URL & Token Refresh
- Frontend tüm isteklerde `VITE_API_BASE` değerini kullanır (bkz. `apps/frontend/src/lib/http.ts`).
- 401 Unauthorized alınırsa otomatik olarak refresh token ile erişim yenilenir ve istek tekrar denenir.
- Geliştirirken farklı backend portu/hostu kullanacaksan `.env.development` içindeki `VITE_API_BASE` değerini güncellemen yeterli.

### Feature Flags
- `VITE_ENABLE_ADMIN_DEMO` (default: `false`)
  - Admin-only rotaları (örn. `/admin-danger`) yerel demoda varsayılan olarak KAPALI.
  - Açmak için: `echo "VITE_ENABLE_ADMIN_DEMO=true" >> apps/frontend/.env.development` ve dev server’ı yeniden başlat.

## Smoke Tests
```bash
# Login
curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"emreaslan663","password":"demo123"}' | tee /tmp/login.json
ACCESS=$(jq -r .access /tmp/login.json)

# Me
curl -i -H "Authorization: Bearer $ACCESS" http://localhost:8000/api/users/me/

# Feed/Posts/Albums
curl -i -H "Authorization: Bearer $ACCESS" "http://localhost:8000/api/feed/posts?page_size=5"
curl -i -H "Authorization: Bearer $ACCESS" "http://localhost:8000/api/posts/?page_size=5"
curl -i -H "Authorization: Bearer $ACCESS" "http://localhost:8000/api/albums/"
```

## Deployment Artifacts (Archived)
Aşağıdaki dosyalar yerel demo odağı için `infra/archive/` altına taşındı:
- `apps/backend/Dockerfile` → `infra/archive/backend.Dockerfile`
- `apps/frontend/Dockerfile` → `infra/archive/frontend.Dockerfile`
- `infra/compose/docker-compose.prod.yml` → `infra/archive/`
- `infra/compose/.env.prod.template` → `infra/archive/`

Not: Bu repo yalnızca yerel demo içindir. Docker/K8s/Prod kurulumları kapsam dışıdır.

## UI Patterns

### ErrorCard Component
Standardized error display with retry functionality across all pages:
- **Props**: `title`, `message`, `details?`, `showRetry?`
- **Emits**: `retry` event for retry button
- **Accessibility**: `role="alert"`, `aria-live="polite"`, focus management
- **Usage**: All pages use `<ErrorCard @retry="fetchAgain" />` for consistent error handling

### State Machine
Each page follows the same pattern:
1. **Loading** → skeleton/loading state
2. **Success** → render data or empty state
3. **Error** → ErrorCard with retry button
4. **Retry** → calls page-specific `fetchAgain()` function (e.g., `fetchFeed()`, `fetchPosts()`, `fetchAlbums()`, `fetchData()`, `fetchTodos()`)
