import { ref } from 'vue'

export function useUndo() {
  const active = ref(false)
  const label = ref('')
  const remainingMs = ref(0)

  let intervalId: number | null = null
  let timeoutId: number | null = null
  let onConfirmRef: null | (() => Promise<void>) = null

  function clearTimers() {
    if (intervalId !== null) {
      clearInterval(intervalId)
      intervalId = null
    }
    if (timeoutId !== null) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
  }

  function cancel() {
    clearTimers()
    active.value = false
    label.value = ''
    remainingMs.value = 0
    onConfirmRef = null
  }

  function showUndo(message: string, onConfirm: () => Promise<void>, ttlMs = 3000) {
    // Cancel existing undo if present
    cancel()

    label.value = message
    remainingMs.value = ttlMs
    active.value = true
    onConfirmRef = onConfirm

    const startedAt = Date.now()
    intervalId = window.setInterval(() => {
      const elapsed = Date.now() - startedAt
      const left = Math.max(0, ttlMs - elapsed)
      remainingMs.value = left
      if (left <= 0) {
        cancel()
      }
    }, 100)

    timeoutId = window.setTimeout(() => {
      cancel()
    }, ttlMs)
  }

  async function confirm() {
    if (!active.value || !onConfirmRef) return
    try {
      await onConfirmRef()
    } finally {
      cancel()
    }
  }

  function dispose() {
    clearTimers()
  }

  return {
    active,
    label,
    remainingMs,
    showUndo,
    cancel,
    dispose,
    // expose confirm for consumer components if needed
    confirm,
  }
}
