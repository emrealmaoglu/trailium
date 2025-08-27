<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  message: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
  },
  duration: {
    type: Number,
    default: 5000
  },
  show: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close'])
const visible = ref(props.show)
const progress = ref(100)

let progressInterval
let closeTimeout

onMounted(() => {
  if (props.duration > 0) {
    const startTime = Date.now()
    const endTime = startTime + props.duration

    progressInterval = setInterval(() => {
      const remaining = endTime - Date.now()
      if (remaining <= 0) {
        close()
      } else {
        progress.value = (remaining / props.duration) * 100
      }
    }, 10)

    closeTimeout = setTimeout(close, props.duration)
  }
})

onUnmounted(() => {
  if (progressInterval) clearInterval(progressInterval)
  if (closeTimeout) clearTimeout(closeTimeout)
})

function close() {
  visible.value = false
  emit('close')
}

const typeStyles = {
  success: {
    bg: '#dcfce7',
    border: '#bbf7d0',
    text: '#166534',
    icon: '✅'
  },
  error: {
    bg: '#fee2e2',
    border: '#fecaca',
    text: '#b91c1c',
    icon: '❌'
  },
  warning: {
    bg: '#fef3c7',
    border: '#fed7aa',
    text: '#d97706',
    icon: '⚠️'
  },
  info: {
    bg: '#dbeafe',
    border: '#bfdbfe',
    text: '#1e40af',
    icon: 'ℹ️'
  }
}

const currentStyle = typeStyles[props.type]
</script>

<template>
  <Transition name="notification">
    <div v-if="visible" class="notification" :style="`background: ${currentStyle.bg}; border: 1px solid ${currentStyle.border}; color: ${currentStyle.text};`">
      <div class="notification-content">
        <span class="notification-icon">{{ currentStyle.icon }}</span>
        <span class="notification-message">{{ message }}</span>
        <button @click="close" class="notification-close" :style="`color: ${currentStyle.text};`">
          ×
        </button>
      </div>
      <div v-if="duration > 0" class="notification-progress" :style="`width: ${progress}%; background: ${currentStyle.text};`"></div>
    </div>
  </Transition>
</template>

<style scoped>
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  max-width: 400px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow: hidden;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
}

.notification-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.notification-message {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
}

.notification-close {
  background: none;
  border: none;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.notification-close:hover {
  background: rgba(0, 0, 0, 0.1);
}

.notification-progress {
  height: 3px;
  transition: width 0.1s linear;
}

/* Transitions */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
