<script setup>
import { ref, onMounted, onUnmounted, inject } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const showShortcuts = ref(false)
const showNotification = inject('showNotification')

const shortcuts = [
  { key: 'g + h', action: 'Go to Home', route: '/' },
  { key: 'g + u', action: 'Go to Users', route: '/users' },
  { key: 'g + t', action: 'Go to Todos', route: '/todos' },
  { key: 'g + p', action: 'Go to Posts', route: '/posts' },
  { key: 'g + a', action: 'Go to Albums', route: '/albums' },
  { key: 'g + f', action: 'Go to Feed', route: '/feed' },
  { key: 'g + s', action: 'Go to Settings', route: '/settings' },
  { key: '?', action: 'Show this help', route: null },
  { key: 'Escape', action: 'Close modals/panels', route: null },
  { key: 'Ctrl/Cmd + k', action: 'Quick search', route: null },
]

let keyBuffer = ''
let keyBufferTimeout = null

function handleKeydown(event) {
  // Don't trigger shortcuts when typing in input fields
  if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
    return
  }

  // Show shortcuts help
  if (event.key === '?') {
    event.preventDefault()
    showShortcuts.value = !showShortcuts.value
    return
  }

  // Close shortcuts help
  if (event.key === 'Escape') {
    showShortcuts.value = false
    return
  }

  // Quick navigation with 'g' key
  if (event.key === 'g') {
    keyBuffer = 'g'
    clearTimeout(keyBufferTimeout)
    keyBufferTimeout = setTimeout(() => {
      keyBuffer = ''
    }, 1000)
    return
  }

  // Handle second key in navigation sequence
  if (keyBuffer === 'g') {
    event.preventDefault()
    const secondKey = event.key.toLowerCase()

    switch (secondKey) {
      case 'h':
        router.push('/')
        // Notification removed - unnecessary success message
        break
      case 'u':
        router.push('/users')
        // Notification removed - unnecessary success message
        break
      case 't':
        router.push('/todos')
        // Notification removed - unnecessary success message
        break
      case 'p':
        router.push('/posts')
        // Notification removed - unnecessary success message
        break
      case 'a':
        router.push('/albums')
        // Notification removed - unnecessary success message
        break
      case 'f':
        router.push('/feed')
        // Notification removed - unnecessary success message
        break
      case 's':
        router.push('/settings')
        // Notification removed - unnecessary success message
        break
    }

    keyBuffer = ''
    clearTimeout(keyBufferTimeout)
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  if (keyBufferTimeout) {
    clearTimeout(keyBufferTimeout)
  }
})
</script>

<template>
  <div v-if="showShortcuts" class="shortcuts-overlay" @click="showShortcuts = false">
    <div class="shortcuts-modal" @click.stop>
      <div class="shortcuts-header">
        <h3>⌨️ Keyboard Shortcuts</h3>
        <button @click="showShortcuts = false" class="close-btn">×</button>
      </div>

      <div class="shortcuts-content">
        <div class="shortcuts-section">
          <h4>🚀 Quick Navigation</h4>
          <div class="shortcuts-grid">
            <div v-for="shortcut in shortcuts.slice(0, 7)" :key="shortcut.key" class="shortcut-item">
              <kbd class="shortcut-key">{{ shortcut.key }}</kbd>
              <span class="shortcut-action">{{ shortcut.action }}</span>
            </div>
          </div>
        </div>

        <div class="shortcuts-section">
          <h4>🔧 General</h4>
          <div class="shortcuts-grid">
            <div v-for="shortcut in shortcuts.slice(7)" :key="shortcut.key" class="shortcut-item">
              <kbd class="shortcut-key">{{ shortcut.key }}</kbd>
              <span class="shortcut-action">{{ shortcut.action }}</span>
            </div>
          </div>
        </div>

        <div class="shortcuts-tip">
          💡 <strong>Tip:</strong> Press <kbd>?</kbd> anytime to show this help
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.shortcuts-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.2s ease;
}

.shortcuts-modal {
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: 16px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

.shortcuts-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--c-border);
}

.shortcuts-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s ease;
  color: var(--c-text-muted);
}

.close-btn:hover {
  background: var(--c-surface-2);
}

.shortcuts-content {
  padding: 24px;
}

.shortcuts-section {
  margin-bottom: 24px;
}

.shortcuts-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--c-text);
}

.shortcuts-grid {
  display: grid;
  gap: 12px;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 8px;
}

.shortcut-key {
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--c-accent);
  font-family: monospace;
  min-width: 60px;
  text-align: center;
}

.shortcut-action {
  font-size: 14px;
  color: var(--c-text);
}

.shortcuts-tip {
  padding: 16px;
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
  border-radius: 8px;
  font-size: 13px;
  color: var(--c-text-muted);
  text-align: center;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
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
  .shortcuts-modal {
    width: 95%;
    margin: 20px;
  }

  .shortcuts-content {
    padding: 16px;
  }

  .shortcut-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
