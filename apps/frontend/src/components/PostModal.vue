<template>
  <div class="overlay" @click.self="$emit('close')">
    <div class="modal">
      <header class="hdr">
        <h3 class="title">{{ post.title }}</h3>
        <button class="close" @click="$emit('close')">×</button>
      </header>
      <div class="content">
        <p class="body">{{ post.body }}</p>
        <div class="likes"><button class="btn" @click="$emit('like', post)">❤️ {{ post.likes_count||0 }}</button></div>
      </div>
      <section class="comments">
        <h4>{{ $t('posts.comments') }}</h4>
        <div v-if="loading" class="skl"></div>
        <CommentRow v-for="c in comments" :key="c.id" :comment="c" />
        <div class="add">
          <input v-model="newBody" :placeholder="$t('posts.addComment') as string" class="inp" @keydown.enter="add" />
          <button class="btn" @click="add">{{ $t('posts.comment') }}</button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
/** Gönderi detay modalı. */
import { ref, onMounted } from 'vue'
import CommentRow from './CommentRow.vue'

const props = defineProps<{ post: any }>()
const emit = defineEmits<{ 'close':[], 'like':[any], 'add-comment':[string] }>()
const comments = ref<any[]>([])
const loading = ref(true)
const newBody = ref('')

async function fetch() {
  loading.value = true
  try {
    const res = await fetch(`${window.location.origin}/api/posts/${props.post.id}/comments/`, { credentials: 'include' })
    comments.value = await res.json()
  } finally {
    loading.value = false
  }
}

function add() {
  const b = newBody.value.trim(); if (!b) return
  emit('add-comment', b)
  newBody.value = ''
  fetch()
}

onMounted(fetch)
</script>

<style scoped>
.overlay { position: fixed; inset: 0; background: rgba(0,0,0,.35); display: grid; place-items: center; }
.modal { width: min(720px, 96vw); background: var(--c-surface); color: var(--c-text); border-radius: 12px; border: 1px solid var(--c-border); padding: 12px; }
.hdr { display: flex; justify-content: space-between; align-items: center; }
.title { margin: 0; font-size: 18px; font-weight: 700; }
.close { border: none; background: transparent; font-size: 20px; cursor: pointer; }
.content { display: grid; gap: 8px; }
.comments { margin-top: 12px; display: grid; gap: 8px; }
.add { display: flex; gap: 8px; }
.inp { flex: 1; border: 1px solid var(--c-border); border-radius: 8px; padding: 8px 10px; }
.btn { border: 1px solid var(--c-border); background: var(--c-surface-2); border-radius: 8px; padding: 6px 10px; }
.skl { height: 60px; border-radius: 8px; background: var(--c-surface-2); animation: pulse 1.2s ease-in-out infinite; }
@keyframes pulse { 0%{opacity:.6} 50%{opacity:.95} 100%{opacity:.6} }
</style>
