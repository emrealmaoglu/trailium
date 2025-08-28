<template>
  <div class="user-menu" @keydown.esc="open = false">
    <button
      class="user-menu-button"
      @click="open = !open"
      aria-haspopup="menu"
      :aria-expanded="open ? 'true' : 'false'"
    >
      <div class="user-avatar">
        <img
          v-if="session.user?.avatar"
          :src="session.user.avatar"
          :alt="session.displayName"
          class="avatar-image"
        />
        <div v-else class="avatar-placeholder">
          {{ session.initials }}
        </div>
      </div>
      <div class="user-info">
        <span class="user-name">{{ session.displayName }}</span>
        <span class="user-email">{{ session.displayEmail }}</span>
      </div>
      <svg class="dropdown-icon" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.06l3.71-3.83a.75.75 0 111.08 1.04l-4.25 4.39a.75.75 0 01-1.08 0L5.21 8.27a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
      </svg>
    </button>

    <div
      v-show="open"
      class="user-dropdown"
      role="menu"
      @click.outside="open = false"
    >
      <div class="dropdown-header">
        <div class="dropdown-avatar">
          <img
            v-if="session.user?.avatar"
            :src="session.user.avatar"
            :alt="session.displayName"
            class="dropdown-avatar-image"
          />
          <div v-else class="dropdown-avatar-placeholder">
            {{ session.initials }}
          </div>
        </div>
        <div class="dropdown-user-info">
          <div class="dropdown-user-name">{{ session.displayName }}</div>
          <div class="dropdown-user-email">{{ session.displayEmail }}</div>
        </div>
      </div>

      <div class="dropdown-divider"></div>

      <div class="dropdown-section">
        <div class="section-title">Theme</div>
        <div class="theme-buttons">
          <button
            :class="['theme-btn', { active: currentTheme === 'light' }]"
            @click="setTheme('light')"
          >
            ☀️ Light
          </button>
          <button
            :class="['theme-btn', { active: currentTheme === 'dark' }]"
            @click="setTheme('dark')"
          >
            🌙 Dark
          </button>
          <button
            :class="['theme-btn', { active: currentTheme === 'system' }]"
            @click="setTheme('system')"
          >
            💻 System
          </button>
        </div>
      </div>

      <div class="dropdown-divider"></div>

      <div class="dropdown-menu">
        <button class="menu-item" @click="goProfile">
          👤 Profile
        </button>
        <button class="menu-item" @click="goSettings">
          ⚙️ Settings
        </button>
      </div>

      <div class="dropdown-divider"></div>

      <button class="logout-button" @click="onLogout">
        🚪 Logout
      </button>
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

const setTheme = (t) => {
  applyTheme(t);
  currentTheme.value = t;
  open.value = false
}

const goProfile = () => {
  open.value = false
  router.push('/profile')
}

const goSettings = () => {
  open.value = false;
  router.push('/settings')
}

const onLogout = async () => {
  open.value = false
  await session.logout()
  router.push('/auth/login')
}
</script>

<style scoped>
.user-menu {
  position: relative;
}

.user-menu-button {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
  border-radius: 12px;
  color: var(--c-text);
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
}

.user-menu-button:hover {
  background: var(--c-surface);
  border-color: var(--c-border);
  transform: translateY(-1px);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid var(--c-border);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: white;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 0;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
  color: var(--c-text);
}

.user-email {
  font-size: 12px;
  color: var(--c-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}

.dropdown-icon {
  width: 16px;
  height: 16px;
  opacity: 0.7;
  transition: transform 0.2s ease;
}

.user-menu-button:hover .dropdown-icon {
  transform: rotate(180deg);
}

.user-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  width: 280px;
  background: var(--c-surface);
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  border: 1px solid var(--c-border);
  overflow: hidden;
  z-index: 1000;
  animation: slideDown 0.2s ease;
  color: var(--c-text);
}

.dropdown-header {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.dropdown-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid rgba(255, 255, 255, 0.3);
  margin-bottom: 12px;
}

.dropdown-avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.dropdown-avatar-placeholder {
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  color: white;
}

.dropdown-user-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.dropdown-user-email {
  font-size: 14px;
  opacity: 0.9;
}

.dropdown-divider {
  height: 1px;
  background: var(--c-border);
  margin: 0;
}

.dropdown-section {
  padding: 16px 20px;
}

.section-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--c-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.theme-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
}

.theme-btn {
  padding: 8px 12px;
  border: 1px solid var(--c-border);
  border-radius: 8px;
  background: var(--c-surface-2);
  color: var(--c-text);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.theme-btn:hover {
  background: var(--c-surface);
  border-color: var(--c-border);
}

.theme-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.dropdown-menu {
  padding: 8px 0;
}

.menu-item {
  width: 100%;
  padding: 12px 20px;
  text-align: left;
  background: none;
  border: none;
  color: var(--c-text);
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.menu-item:hover {
  background: var(--c-surface-2);
}

.logout-button {
  width: 100%;
  padding: 16px 20px;
  text-align: left;
  background: none;
  border: none;
  color: #dc2626;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s ease;
}

.logout-button:hover {
  background: #fef2f2;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* App dark mode overrides (root has .dark class) */
:global(.dark) .user-menu-button {
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
  color: var(--c-text);
}

:global(.dark) .user-menu-button:hover {
  background: var(--c-surface);
  border-color: var(--c-border);
}

:global(.dark) .user-avatar {
  border: 2px solid var(--c-border);
}
</style>
