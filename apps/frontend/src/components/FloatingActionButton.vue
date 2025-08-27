<script setup>
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const showMenu = ref(false)
const showNotification = inject('showNotification')

function toggleMenu() {
  showMenu.value = !showMenu.value
}

function navigateTo(route, action) {
  router.push(route)
  showMenu.value = false
}

function closeMenu() {
  showMenu.value = false
}

// Close menu when clicking outside
function handleClickOutside(event) {
  if (!event.target.closest('.fab-container')) {
    showMenu.value = false
  }
}
</script>

<template>
  <div class="fab-container">
    <!-- Main FAB Button -->
    <button
      @click="toggleMenu"
      class="fab-main"
      :class="{ 'fab-active': showMenu }"
      title="Quick Actions"
    >
      <span v-if="!showMenu">⚡</span>
      <span v-else>×</span>
    </button>

    <!-- FAB Menu -->
    <div v-if="showMenu" class="fab-menu">
      <div class="fab-menu-item" @click="navigateTo('/posts', 'Creating new post...')">
        <span class="fab-icon">📝</span>
        <span class="fab-label">New Post</span>
      </div>

      <div class="fab-menu-item" @click="navigateTo('/albums', 'Opening photo albums...')">
        <span class="fab-icon">📸</span>
        <span class="fab-label">Upload Photos</span>
      </div>

      <div class="fab-menu-item" @click="navigateTo('/todos', 'Managing todos...')">
        <span class="fab-icon">✅</span>
        <span class="fab-label">Add Todo</span>
      </div>

      <div class="fab-menu-item" @click="navigateTo('/users', 'Browsing users...')">
        <span class="fab-icon">👥</span>
        <span class="fab-label">Find Users</span>
      </div>

      <div class="fab-menu-item" @click="navigateTo('/feed', 'Viewing your feed...')">
        <span class="fab-icon">🔄</span>
        <span class="fab-label">View Feed</span>
      </div>
    </div>

    <!-- Backdrop -->
    <div v-if="showMenu" class="fab-backdrop" @click="closeMenu"></div>
  </div>
</template>

<style scoped>
.fab-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
}

.fab-main {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--c-accent);
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(95, 55, 210, 0.4);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.fab-main:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(95, 55, 210, 0.6);
}

.fab-main.fab-active {
  background: #ef4444;
  transform: rotate(45deg);
}

.fab-menu {
  position: absolute;
  bottom: 70px;
  right: 0;
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: 16px;
  padding: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  animation: slideUp 0.3s ease;
  min-width: 200px;
}

.fab-menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s ease;
  color: var(--c-text);
}

.fab-menu-item:hover {
  background: var(--c-surface-2);
  transform: translateX(-4px);
}

.fab-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.fab-label {
  font-size: 14px;
  font-weight: 500;
}

.fab-backdrop {
  position: fixed;
  inset: 0;
  z-index: 999;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .fab-container {
    bottom: 16px;
    right: 16px;
  }

  .fab-main {
    width: 48px;
    height: 48px;
    font-size: 20px;
  }

  .fab-menu {
    bottom: 60px;
    right: -8px;
    min-width: 180px;
  }
}
</style>
