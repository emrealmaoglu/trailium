<script setup>
import { ref, provide, onMounted } from 'vue'
import { useSessionStore } from '@/stores/session'
import AppShell from './layouts/AppShell.vue'
import KeyboardShortcuts from './components/KeyboardShortcuts.vue'
import FloatingActionButton from './components/FloatingActionButton.vue'

const session = useSessionStore()

// Global notification system
const notifications = ref([])
let notificationCounter = 0

// Generate unique ID for notifications
function generateNotificationId() {
  return `notification-${Date.now()}-${++notificationCounter}`
}

function showNotification(message, type = 'info', duration = 5000) {
  const id = generateNotificationId()
  const notification = {
    id,
    message,
    type,
    duration,
    timestamp: Date.now()
  }

  notifications.value.push(notification)

  // Auto-remove notification after duration
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

function clearAllNotifications() {
  notifications.value = []
}

// Provide notification system to all components
provide('showNotification', showNotification)
provide('removeNotification', removeNotification)
provide('clearAllNotifications', clearAllNotifications)

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
      <!-- Notification Header -->
      <div v-if="notifications.length > 0" class="notifications-header">
        <span class="notifications-count">{{ notifications.length }} notification(s)</span>
        <button
          @click="clearAllNotifications"
          class="clear-all-btn"
          title="Clear all notifications"
        >
          Clear All
        </button>
      </div>

      <!-- Individual Notifications -->
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
            title="Dismiss notification"
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
  color: #333;
  background-color: #f5f5f5;
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
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.auth-container {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 500px;
  text-align: center;
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
  color: #1a1a1a;
  margin: 0;
}

.auth-subtitle {
  color: #6b7280;
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
  color: #9ca3af;
  font-size: 14px;
  margin: 0;
}

/* Enhanced Notifications */
.notifications-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 400px;
  max-height: 80vh;
  overflow-y: auto;
}

.notifications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-size: 12px;
  color: #6b7280;
}

.notifications-count {
  font-weight: 500;
}

.clear-all-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  transition: all 0.2s ease;
}

.clear-all-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #374151;
}

.notification-item {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  animation: slideIn 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.1);
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

.notification-info {
  border-left: 4px solid #3b82f6;
}

.notification-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
}

.notification-icon {
  font-size: 18px;
  flex-shrink: 0;
  margin-top: 2px;
}

.notification-message {
  flex: 1;
  font-size: 14px;
  line-height: 1.4;
  word-wrap: break-word;
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
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
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
  .auth-container {
    background: #1f2937;
    color: white;
  }

  .logo-text {
    color: white;
  }

  .auth-subtitle {
    color: #9ca3af;
  }

  .auth-footer {
    border-top-color: #4b5563;
  }

  .auth-footer p {
    color: #6b7280;
  }

  .notifications-header {
    background: rgba(31, 41, 55, 0.95);
    color: #9ca3af;
    border-color: rgba(255, 255, 255, 0.1);
  }

  .notification-item {
    background: #1f2937;
    color: white;
    border-color: rgba(255, 255, 255, 0.1);
  }

  .notification-close:hover {
    background: #374151;
    color: #d1d5db;
  }
}

/* Responsive notifications */
@media (max-width: 768px) {
  .notifications-container {
    left: 20px;
    right: 20px;
    max-width: none;
  }

  .notification-content {
    padding: 12px;
  }

  .notification-message {
    font-size: 13px;
  }
}
</style>
