<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  color: {
    type: String,
    default: 'var(--c-accent)'
  }
})

const spinnerSize = computed(() => {
  switch (props.size) {
    case 'small': return '16px'
    case 'large': return '32px'
    default: return '24px'
  }
})
</script>

<template>
  <div class="spinner" :style="`width: ${spinnerSize}; height: ${spinnerSize};`">
    <svg viewBox="0 0 24 24" :style="`color: ${color};`">
      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" opacity="0.25" />
      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" class="spinner-circle" />
    </svg>
  </div>
</template>

<style scoped>
.spinner {
  display: inline-block;
}

.spinner svg {
  width: 100%;
  height: 100%;
  animation: spin 1s linear infinite;
}

.spinner-circle {
  stroke-dasharray: 63;
  stroke-dashoffset: 63;
  animation: dash 1.5s ease-in-out infinite;
}

@keyframes spin {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dash {
  0% {
    stroke-dashoffset: 63;
  }
  50% {
    stroke-dashoffset: 15.75;
  }
  100% {
    stroke-dashoffset: 63;
  }
}
</style>
