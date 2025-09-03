<template>
  <nav class="pagination" role="navigation" aria-label="Pagination">
    <button
      class="btn"
      :disabled="disabled || page <= 1"
      @click="$emit('update:page', Math.max(1, page - 1))"
      :aria-label="$t('users.pagination.prev') as string"
    >
      {{ $t('users.pagination.prev') }}
    </button>

    <span class="info" aria-live="polite">{{ page }} / {{ totalPages }}</span>

    <button
      class="btn"
      :disabled="disabled || page >= totalPages"
      @click="$emit('update:page', Math.min(totalPages, page + 1))"
      :aria-label="$t('users.pagination.next') as string"
    >
      {{ $t('users.pagination.next') }}
    </button>
  </nav>
</template>

<script setup lang="ts">
/** Basit sayfalama bileşeni. */
defineProps<{ page: number; totalPages: number; disabled?: boolean }>()
defineEmits<{ 'update:page': [value: number] }>()
</script>

<style scoped>
.pagination { display: flex; gap: 12px; align-items: center; }
.btn { padding: 8px 12px; border: 1px solid var(--c-border); border-radius: 8px; background: var(--c-surface); }
.btn[disabled] { opacity: .5; cursor: not-allowed; }
.info { color: var(--c-text-muted); font-size: 14px; }
</style>
