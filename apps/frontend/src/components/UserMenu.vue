<template>
  <div class="relative" @keydown.esc="open=false">
    <button
      class="flex items-center gap-2 rounded-full px-3 py-1.5 ring-1 ring-black/10 hover:bg-black/5 focus:outline-none focus-visible:ring-2"
      @click="open=!open"
      aria-haspopup="menu"
      :aria-expanded="open ? 'true' : 'false'"
    >
      <span class="inline-flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-pink-500 to-cyan-500 text-white text-sm font-semibold">
        {{ session.initials }}
      </span>
      <span class="hidden sm:block text-sm text-gray-700 dark:text-gray-200 truncate max-w-[14rem]">{{ session.displayEmail || session.displayName }}</span>
      <svg class="h-4 w-4 opacity-70" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.06l3.71-3.83a.75.75 0 111.08 1.04l-4.25 4.39a.75.75 0 01-1.08 0L5.21 8.27a.75.75 0 01.02-1.06z" clip-rule="evenodd"/></svg>
    </button>

    <div
      v-show="open"
      class="absolute right-0 z-40 mt-2 w-64 overflow-hidden rounded-xl border border-black/10 bg-white shadow-lg ring-1 ring-black/5 dark:bg-zinc-900"
      role="menu"
      @click.outside="open=false"
    >
      <div class="px-4 py-3 text-sm">
        <div class="font-medium">{{ session.displayName }}</div>
        <div class="text-gray-500 truncate">{{ session.displayEmail }}</div>
      </div>
      <div class="h-px bg-black/10"></div>

      <div class="px-4 py-2">
        <div class="text-xs uppercase tracking-wide text-gray-500 mb-1">Theme</div>
        <div class="grid grid-cols-3 gap-2">
          <button :class="btnClass('light')" @click="setTheme('light')">Light</button>
          <button :class="btnClass('dark')" @click="setTheme('dark')">Dark</button>
          <button :class="btnClass('system')" @click="setTheme('system')">System</button>
        </div>
      </div>

      <div class="h-px bg-black/10"></div>
      <button class="w-full px-4 py-2 text-left text-sm hover:bg-black/5" role="menuitem" @click="goProfile">Profile (coming soon)</button>
      <button class="w-full px-4 py-2 text-left text-sm hover:bg-black/5" role="menuitem" @click="goSettings">Settings (coming soon)</button>
      <div class="h-px bg-black/10"></div>
      <button class="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50" role="menuitem" @click="onLogout">Logout</button>
    </div>
  </div>
</template>

<script setup lang="js">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { applyTheme, getStoredTheme } from '@/lib/theme'

const router = useRouter()
const session = useSessionStore()
const open = ref(false)
const currentTheme = ref(getStoredTheme())

const setTheme = (t) => { applyTheme(t); currentTheme.value = t; open.value = false }
const btnClass = (t) => currentTheme.value === t
  ? 'btn-ghost btn-active'
  : 'btn-ghost'
const goProfile = () => { open.value = false }
const goSettings = () => { open.value = false }
const onLogout = async () => {
  open.value = false
  await session.logout()
  router.push('/auth/login')
}
</script>

<style scoped>
.btn-ghost{ border-radius:0.5rem; border:1px solid rgba(0,0,0,0.1); padding:0.25rem 0.5rem; font-size:0.875rem; }
.btn-ghost:hover{ background:rgba(0,0,0,0.05); }
.btn-active{ border-color: rgba(0,0,0,0.4); background: rgba(0,0,0,0.05); }
@media (prefers-color-scheme: dark){
  .btn-ghost{ border-color: rgba(255,255,255,0.1); }
  .btn-active{ border-color: rgba(255,255,255,0.4); background: rgba(255,255,255,0.1); }
}
</style>


