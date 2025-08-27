<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import logoSrc from '../assets/brand/N2Mobil-Logotype.png'
import { useSessionStore } from '@/stores/session'
import UserMenu from '@/components/UserMenu.vue'

const session = useSessionStore()
const isDark = ref(true)

function applyTheme(dark) {
  const root = document.documentElement
  root.classList.toggle('theme-dark', dark)
}

function loadInitialTheme() {
  const saved = localStorage.getItem('theme')
  if (saved === 'dark' || saved === 'light') {
    isDark.value = saved === 'dark'
  } else {
    isDark.value = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
  }
  applyTheme(isDark.value)
}

function toggleTheme() {
  isDark.value = !isDark.value
  applyTheme(isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

onMounted(loadInitialTheme)
</script>

<template>
  <div style="min-height:100vh; background:var(--c-bg); color:var(--c-text); display:flex; flex-direction:column;">
    <header style="display:flex; align-items:center; justify-content:space-between; padding:12px 24px; border-bottom:1px solid var(--c-border);">
      <strong style="font-weight:600; letter-spacing:.02em;">Trailium</strong>
      <div style="display:flex; gap:8px; align-items:center;">
        <UserMenu />
      </div>
    </header>

    <div style="display:flex; flex:1; min-height:0;">
      <aside style="width:240px; border-right:1px solid var(--c-border); padding:12px; display:flex; flex-direction:column; justify-content:space-between;">
        <nav class="side__nav">
          <RouterLink to="/users" class="nav__a" active-class="is-active">Users</RouterLink>
          <RouterLink to="/todos" class="nav__a" active-class="is-active">Todos</RouterLink>
          <RouterLink to="/posts" class="nav__a" active-class="is-active">Posts</RouterLink>
          <RouterLink to="/albums" class="nav__a" active-class="is-active">Albums</RouterLink>
        </nav>
        <!-- bottom-left full logotype -->
        <div style="padding:8px 4px;">
          <img :src="logoSrc" alt="N2Mobil Logotype" style="object-fit:contain; object-position:left; max-width:100%; height:auto; display:block;" />
        </div>
      </aside>
      <main style="flex:1; padding:24px;">
        <div style="max-width:1120px; margin:0 auto; width:100%;">
          <RouterView />
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.side__nav { display:grid; gap:4px; }
.nav__a { padding:8px 10px; border-radius:10px; color:var(--c-text-muted); text-decoration:none; display:block; border-left:3px solid transparent; }
.nav__a:hover { background:var(--c-surface-2); color:var(--c-text); }
.nav__a.is-active { background:var(--c-surface-2); color:var(--c-text); font-weight:600; border-left-color: var(--c-accent); }
.nav__a:focus { outline: 2px solid var(--c-accent); outline-offset: 2px; }
</style>


