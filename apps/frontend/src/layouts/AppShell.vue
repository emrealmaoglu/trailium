<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ref, inject, computed } from 'vue'
import { useSessionStore } from '@/stores/session'
import logoSrc from '../assets/brand/N2Mobil-Logotype.png'
import UserMenu from '@/components/UserMenu.vue'

const sessionStore = useSessionStore()
const showNotification = inject('showNotification')

// Computed
const isAdmin = computed(() => sessionStore.user?.is_superuser)
const ADMIN_DEMO = String(import.meta.env.VITE_ENABLE_ADMIN_DEMO).toLowerCase() === 'true'
</script>

<template>
  <div style="min-height:100vh; background:var(--c-bg); color:var(--c-text); display:flex; flex-direction:column;">
    <header style="display:flex; align-items:center; justify-content:space-between; padding:12px 24px; border-bottom:1px solid var(--c-border); background:var(--c-surface);">
      <div style="display:flex; align-items:center; gap:16px;">
        <strong style="font-weight:600; letter-spacing:.02em; font-size:18px;">Trailium</strong>
      </div>
      <div style="display:flex; gap:8px; align-items:center;">
        <UserMenu />
      </div>
    </header>

    <div style="display:flex; flex:1; min-height:0;">
      <aside style="width:240px; border-right:1px solid var(--c-border); padding:12px; display:flex; flex-direction:column; justify-content:space-between; background:var(--c-surface);">
        <nav class="side__nav">
          <RouterLink to="/feed" class="nav__a" active-class="is-active">
            🏠 Feed
          </RouterLink>
          <RouterLink to="/users" class="nav__a" active-class="is-active">
            👥 Users
          </RouterLink>
          <RouterLink to="/todos" class="nav__a" active-class="is-active">
            ✅ Todos
          </RouterLink>
          <RouterLink to="/posts" class="nav__a" active-class="is-active">
            📝 Posts
          </RouterLink>
          <RouterLink to="/albums" class="nav__a" active-class="is-active">
            📸 Albums
          </RouterLink>

          <!-- Admin Only Links (hidden unless env flag enabled) -->
          <div v-if="isAdmin && ADMIN_DEMO" style="margin-top: 16px;">
            <div style="margin-bottom: 8px; padding: 8px 12px; background: #fef2f2; border-radius: 8px; border: 1px solid #fecaca;">
              <div style="font-size: 12px; color: #991b1b; margin-bottom: 4px;">Admin Tools</div>
            </div>
            <RouterLink to="/admin-danger" class="nav__a" active-class="is-active">
              ⚠️ Admin Danger
            </RouterLink>
          </div>
        </nav>

        <div style="padding:12px; border-top:1px solid var(--c-border); margin-top:auto;">
          <RouterLink to="/settings" class="nav__a" active-class="is-active">
            ⚙️ Settings
          </RouterLink>
        </div>

        <!-- bottom-left full logotype -->
        <div style="padding:8px 4px;">
          <img :src="logoSrc" alt="N2Mobil Logotype" style="object-fit:contain; object-position:left; max-width:100%; height:auto; display:block;" />
        </div>
      </aside>

      <main style="flex:1; padding:24px; overflow-y:auto;">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.side__nav { display:grid; gap:4px; }
.nav__a { padding:12px 14px; border-radius:10px; color:var(--c-text-muted); text-decoration:none; display:block; border-left:3px solid transparent; transition:all 0.2s ease; }
.nav__a:hover { background:var(--c-surface-2); color:var(--c-text); transform:translateX(4px); }
.nav__a.is-active { background:var(--c-surface-2); color:var(--c-text); font-weight:600; border-left-color: var(--c-accent); }

.quick-action-btn {
  padding:8px 16px;
  background:var(--c-surface);
  border:1px solid var(--c-border);
  border-radius:8px;
  color:var(--c-text);
  text-decoration:none;
  font-size:13px;
  font-weight:500;
  transition:all 0.2s ease;
  white-space:nowrap;
}

.quick-action-btn:hover {
  background:var(--c-accent);
  color:white;
  border-color:var(--c-accent);
  transform:translateY(-2px);
  box-shadow:0 4px 12px rgba(95,55,210,0.3);
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
