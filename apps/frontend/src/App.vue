<script setup>
import { ref, provide, onMounted } from 'vue'
import { useSessionStore } from '@/stores/session'
import AppShell from './layouts/AppShell.vue'
import KeyboardShortcuts from './components/KeyboardShortcuts.vue'
import FloatingActionButton from './components/FloatingActionButton.vue'

const session = useSessionStore()

// Global notification system
const notifications = ref([])

function showNotification(message, type = 'info', duration = 5000) {
  const id = Date.now() + Math.random()
  const notification = { id, message, type, duration }
  notifications.value.push(notification)

  if (duration > 0) {
    setTimeout(() => {
      removeNotification(id)
    }, duration)
  }

  return id
}

function removeNotification(id) {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index > -1) {
    notifications.value.splice(index, 1)
  }
}

// Provide notification system to all components
provide('showNotification', showNotification)
provide('removeNotification', removeNotification)

// Load session from storage on mount
onMounted(() => {
  console.log('App.vue mounted')
  try {
    session.loadFromStorage()
    if (session.access) {
      session.fetchMe()
    }
  } catch (error) {
    console.error('Error in onMounted:', error)
  }
})
</script>

<template>
  <div id="app">
    <!-- Show layout only when user is logged in -->
    <div v-if="session.isLoggedIn" class="authenticated-layout">
      <AppShell />
      <KeyboardShortcuts />
      <FloatingActionButton />
    </div>

    <!-- Show auth layout when not logged in -->
    <div v-else class="auth-layout">
      <div class="auth-container">
        <div class="auth-header">
          <div class="logo">
            <span class="logo-icon">🚀</span>
            <h1 class="logo-text">Trailium</h1>
          </div>
          <p class="auth-subtitle">Welcome to Trailium - Your Social Platform</p>
        </div>

        <div class="auth-content">
          <router-view />
        </div>

        <div class="auth-footer">
          <p>© 2025 Trailium. All rights reserved.</p>
        </div>
      </div>
    </div>

    <!-- Global Notifications -->
    <div class="notifications-container">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="notification-item"
        :class="`notification-${notification.type}`"
      >
        <div class="notification-content">
          <span class="notification-icon">
            {{ notification.type === 'success' ? '✅' :
               notification.type === 'error' ? '❌' :
               notification.type === 'warning' ? '⚠️' : 'ℹ️' }}
          </span>
          <span class="notification-message">{{ notification.message }}</span>
          <button
            @click="removeNotification(notification.id)"
            class="notification-close"
          >
            ×
          </button>
        </div>
        <div class="notification-progress"></div>
      </div>
    </div>
  </div>
</template>

<style>
/* Base styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  line-height: 1.6;
  color: #111; /* improved default text contrast */
  background-color: #f3f4f6; /* softer gray for unauth layout */
}

#app {
  min-height: 100vh;
}

/* Layout styles */
.authenticated-layout {
  min-height: 100vh;
}

.auth-layout {
  min-height: 100vh;
  background: #f3f4f6; /* gray background for contrast */
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.auth-container {
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 500px;
  text-align: center;
  color: #111; /* ensure readable text */
}

.auth-container a {
  color: #2563eb; /* accessible link color */
  text-decoration: none;
}

.auth-container a:hover {
  color: #1d4ed8;
  text-decoration: underline;
}

.auth-header {
  margin-bottom: 32px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
}

.logo-icon {
  font-size: 32px;
}

.logo-text {
  font-size: 28px;
  font-weight: 700;
  color: #111111;
  margin: 0;
}

.auth-subtitle {
  color: #374151; /* darker muted for readability */
  font-size: 16px;
  margin: 0;
}

.auth-content {
  margin-bottom: 32px;
}

.auth-footer {
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

.auth-footer p {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
}

/* Notifications */
.notifications-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 400px;
}

.notification-item {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  animation: slideIn 0.3s ease;
}

.notification-success {
  border-left: 4px solid #10b981;
}

.notification-error {
  border-left: 4px solid #ef4444;
}

.notification-warning {
  border-left: 4px solid #f59e0b;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
}

.notification-icon {
  font-size: 18px;
}

.notification-message {
  flex: 1;
  font-size: 14px;
}

.notification-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #6b7280;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.notification-close:hover {
  background: #f3f4f6;
  color: #374151;
}

.notification-progress {
  height: 3px;
  background: #e5e7eb;
  animation: progress 5s linear;
}

/* Animations */
@keyframes progress {
  from { width: 100%; }
  to { width: 0%; }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Dark theme support */
@media (prefers-color-scheme: dark) {
  .auth-layout {
    background: #0f172a;
  }
  .auth-container {
    background: #1f2937;
    color: #ffffff;
  }
  .logo-text {
    color: #ffffff;
  }
  .auth-subtitle {
    color: #cbd5e1;
  }
  .auth-footer {
    border-top-color: #4b5563;
  }
  .auth-footer p {
    color: #9ca3af;
  }
}
</style>
