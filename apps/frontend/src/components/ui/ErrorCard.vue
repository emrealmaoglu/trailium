<script setup lang="ts">
import { onMounted, ref } from 'vue'

const props = withDefaults(defineProps<{
  title?: string
  message: string
  details?: string
  showRetry?: boolean
}>(), {
  title: 'Error',
  showRetry: false
})

const emit = defineEmits<{
  (e: 'retry'): void
}>()

const containerRef = ref<HTMLElement>()

onMounted(() => {
  // Focus the error container for screen readers
  if (containerRef.value) {
    containerRef.value.focus()
  }
})

function handleRetry() {
  emit('retry')
}
</script>

<template>
  <div
    ref="containerRef"
    role="alert"
    aria-live="polite"
    tabindex="-1"
    class="card"
    style="padding: 24px; background: var(--c-surface); color: var(--c-text); border: 1px solid var(--c-border); box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
  >
    <div style="display: flex; align-items: flex-start; gap: 12px;">
      <div style="font-size: 24px; margin-top: 2px;">⚠️</div>
      <div style="flex: 1;">
        <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 600; color: var(--c-text);">
          {{ props.title }}
        </h3>
        <p style="margin: 0 0 12px 0; font-size: 14px; color: var(--c-text-muted); line-height: 1.5;">
          {{ props.message }}
        </p>
        <p v-if="props.details" style="margin: 0 0 16px 0; font-size: 12px; color: var(--c-text-muted); font-family: monospace; background: var(--c-surface-2); padding: 8px; border-radius: 6px; border: 1px solid var(--c-border);">
          {{ props.details }}
        </p>
        <button
          v-if="props.showRetry"
          @click="handleRetry"
          style="border: 1px solid var(--c-accent); background: var(--c-accent); color: white; border-radius: 8px; padding: 8px 16px; cursor: pointer; font-size: 14px; font-weight: 500; transition: all 0.2s ease;"
          :style="{ 'box-shadow': '0 0 0 2px var(--c-accent), 0 0 0 4px rgba(59, 130, 246, 0.1)' }"
          @focus="(e) => e.target.style.boxShadow = '0 0 0 2px var(--c-accent), 0 0 0 4px rgba(59, 130, 246, 0.3)'"
          @blur="(e) => e.target.style.boxShadow = '0 0 0 2px var(--c-accent), 0 0 0 4px rgba(59, 130, 246, 0.1)'"
        >
          Retry
        </button>
        <slot />
      </div>
    </div>
  </div>
</template>
