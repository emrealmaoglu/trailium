<template>
  <figure class="thumb">
    <img :src="src" :alt="title || 'photo'" />
    <figcaption v-if="title" class="cap">{{ title }}</figcaption>
  </figure>
</template>

<script setup lang="ts">
/** Fotoğraf küçük görseli. */
defineProps<{ src: string; title?: string }>()
</script>

<style scoped>
.thumb { border: 1px solid var(--c-border); border-radius: 10px; overflow: hidden; background: var(--c-surface-2); }
img { width: 100%; height: 100%; object-fit: cover; display: block; }
.cap { font-size: 11px; color: var(--c-text-muted); padding: 4px 6px; }
</style>
