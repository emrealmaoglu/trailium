<template>
  <article class="card" @click="$emit('open', album)" role="button" tabindex="0" @keydown.enter="$emit('open', album)">
    <h3 class="title">{{ album.title }}</h3>
    <div class="muted">{{ (album.photos?.length ?? album.photos_count ?? 0) }} {{ $t('albums.photos') }}</div>
  </article>
</template>

<script setup lang="ts">
/** Albüm kartı. */
defineProps<{ album: any }>()
defineEmits(['open'])
</script>

<style scoped>
.card { border: 1px solid var(--c-border); border-radius: 12px; padding: 12px; background: var(--c-surface); display: grid; gap: 8px; }
.title { margin: 0; font-size: 16px; font-weight: 700; }
.muted { font-size: 12px; color: var(--c-text-muted); }
</style>


