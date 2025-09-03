<template>
  <div class="row">
    <div class="author">@{{ comment.user?.username }}</div>
    <div class="body">{{ comment.body }}</div>
  </div>
</template>

<script setup lang="ts">
/** Basit yorum satırı. */
defineProps<{ comment: any }>()
</script>

<style scoped>
.row { display: grid; grid-template-columns: auto 1fr; gap: 8px; align-items: start; }
.author { font-size: 12px; color: var(--c-text-muted); }
.body { font-size: 14px; }
</style>
