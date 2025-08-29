<template>
  <article class="card">
    <header class="hdr">
      <h3 class="title">{{ post.title }}</h3>
      <button class="like" @click="$emit('like', post)">❤️ {{ post.likes_count || 0 }}</button>
    </header>
    <p class="body">{{ truncated }}</p>
    <footer class="ftr">
      <button class="btn" @click="$emit('open', post)">{{ $t('posts.seeMore') }}</button>
      <span class="muted">{{ (post.comments_count||0) }} {{ $t('posts.comments') }}</span>
    </footer>
  </article>
</template>

<script setup lang="ts">
/** Gönderi kartı. */
import { computed } from 'vue'
const props = defineProps<{ post: any }>()
const truncated = computed(() => (props.post.body || '').slice(0, 180) + ((props.post.body||'').length>180 ? '…' : ''))
defineEmits(['open','like'])
</script>

<style scoped>
.card { border: 1px solid var(--c-border); border-radius: 12px; padding: 12px; background: var(--c-surface); display: grid; gap: 8px; }
.hdr { display: flex; justify-content: space-between; align-items: center; }
.title { margin: 0; font-size: 16px; font-weight: 700; }
.body { margin: 0; color: var(--c-text); }
.ftr { display: flex; justify-content: space-between; align-items: center; }
.btn, .like { border: 1px solid var(--c-border); background: var(--c-surface-2); border-radius: 8px; padding: 6px 10px; }
.muted { font-size: 12px; color: var(--c-text-muted); }
</style>


