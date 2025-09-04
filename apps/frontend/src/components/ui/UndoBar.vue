<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps<{ label: string; ttlMs?: number }>()
const emit = defineEmits<{ (e: 'confirm'): void; (e: 'cancel'): void }>()

const total = props.ttlMs ?? 3000
const start = Date.now()
let raf: number | null = null

const remainingText = computed(() => {
  const left = Math.max(0, total - (Date.now() - start))
  return (left / 1000).toFixed(1)
})

function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    emit('cancel')
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  if (raf) cancelAnimationFrame(raf)
})
</script>

<template>
  <div
    role="status"
    aria-live="polite"
    style="position:fixed; left:0; right:0; bottom:16px; display:flex; justify-content:center; z-index:1100;"
  >
    <div
      class="card"
      style="display:flex; align-items:center; gap:12px; padding:12px 16px; background:var(--c-surface); color:var(--c-text); border:1px solid var(--c-border); box-shadow:0 8px 20px rgba(0,0,0,0.12);"
    >
      <div style="font-size:14px;">{{ props.label }}</div>
      <div style="font-size:12px; color:var(--c-text-muted);">Undo ({{ remainingText }}s)</div>
      <div style="display:flex; gap:8px; margin-left:12px;">
        <button
          @click="$emit('confirm')"
          style="border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:8px; padding:6px 10px; font-size:12px; cursor:pointer;"
        >Undo</button>
        <button
          @click="$emit('cancel')"
          style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:8px; padding:6px 10px; font-size:12px; cursor:pointer;"
        >Dismiss</button>
      </div>
    </div>
  </div>
</template>
