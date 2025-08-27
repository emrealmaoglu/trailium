<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { json } from '@/lib/http'

const loading = ref(true)
const errorMsg = ref('')
const results = ref([])
const next = ref(null)
const modalOpen = ref(false)
const activePost = ref(null)
const comments = ref([])
const adding = ref(false)
const commentBody = ref('')

async function fetchPosts(url = '/api/posts/') {
  loading.value = true
  errorMsg.value = ''
  try {
    const payload = await json(url)
    results.value = payload.results || []
    next.value = payload.next
  } catch (e) {
    errorMsg.value = 'Could not load posts.'
  } finally {
    loading.value = false
  }
}

async function openPost(post) {
  activePost.value = post
  modalOpen.value = true
  comments.value = []
  try {
    comments.value = await json(`/api/posts/${post.id}/comments/`)
  } catch {}
}

async function addComment() {
  if (!activePost.value || !commentBody.value.trim()) return
  adding.value = true
  const body = commentBody.value
  commentBody.value = ''
  try {
    comments.value.unshift({ id: Math.random(), user: { username: 'You' }, body, created_at: new Date().toISOString() })
    await json(`/api/posts/${activePost.value.id}/comments/`, { method: 'POST', body: JSON.stringify({ body }) })
  } catch {
    // revert on error
    comments.value.shift()
  } finally {
    adding.value = false
  }
}

async function toggleLike(post) {
  post._liking = true
  const likedBefore = post._liked || false
  const delta = likedBefore ? -1 : 1
  post.likes_count = (post.likes_count || 0) + delta
  post._liked = !likedBefore
  try {
    const method = likedBefore ? 'DELETE' : 'POST'
    await json(`/api/posts/${post.id}/like/`, { method })
  } catch {
    // revert
    post.likes_count = (post.likes_count || 0) - delta
    post._liked = likedBefore
  } finally {
    post._liking = false
  }
}

onMounted(() => {
  fetchPosts()
  const onVis = () => { if (document.visibilityState === 'visible') fetchPosts() }
  document.addEventListener('visibilitychange', onVis)
  onUnmounted(() => document.removeEventListener('visibilitychange', onVis))
})
</script>

<template>
  <div class="container">
    <div style="display:flex; align-items:center; gap:8px; margin:0 0 16px;">
      <h2 style="margin:0; font-size:22px; font-weight:700;">Posts</h2>
      <button @click="fetchPosts()" style="margin-left:auto; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:6px 10px; cursor:pointer; font-size:13px;">Refresh</button>
    </div>

    <div v-if="loading" class="card" style="padding:16px;">Loading…</div>
    <div v-else-if="errorMsg" class="card" style="padding:16px; color:var(--c-text-muted);">{{ errorMsg }}</div>
    <div v-else class="grid grid-cols-responsive" style="gap:12px;">
      <div v-for="p in results" :key="p.id" class="card" style="padding:16px; display:grid; gap:8px;">
        <div style="font-weight:700; font-size:16px;">{{ p.title }}</div>
        <div style="color:var(--c-text-muted); font-size:14px;">{{ p.body?.slice(0, 140) }}</div>
        <div style="display:flex; gap:10px; align-items:center; font-size:13px; color:var(--c-text-muted);">
          <span>❤ {{ p.likes_count || 0 }}</span>
          <span>💬 {{ p.comments_count || 0 }}</span>
          <button :disabled="p._liking" @click="toggleLike(p)" style="margin-left:auto; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:4px 8px; cursor:pointer; font-size:12px;">{{ p._liked ? 'Unlike' : 'Like' }}</button>
          <button @click="openPost(p)" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:4px 8px; cursor:pointer; font-size:12px;">Details</button>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="modalOpen" style="position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; padding:20px;">
      <div class="card" style="width:100%; max-width:720px; background:var(--c-bg); color:var(--c-text); border:1px solid var(--c-border); border-radius:16px; padding:16px;">
        <div style="display:flex; align-items:center;">
          <div style="font-weight:700; font-size:18px;">{{ activePost?.title }}</div>
          <button @click="modalOpen=false" style="margin-left:auto; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:4px 8px; cursor:pointer; font-size:12px;">Close</button>
        </div>
        <div style="margin-top:8px; font-size:14px; color:var(--c-text); white-space:pre-wrap;">{{ activePost?.body }}</div>

        <div style="margin-top:16px; font-weight:700;">Comments</div>
        <div v-if="comments.length===0" style="color:var(--c-text-muted); font-size:13px;">No comments yet.</div>
        <ul style="list-style:none; padding:0; margin:8px 0; display:grid; gap:10px;">
          <li v-for="c in comments" :key="c.id" class="card" style="padding:10px;">
            <div style="font-size:13px; color:var(--c-text);">{{ c.user?.username || 'User' }}</div>
            <div style="font-size:14px; color:var(--c-text);">{{ c.body }}</div>
          </li>
        </ul>

        <form @submit.prevent="addComment" style="display:flex; gap:8px;">
          <input v-model="commentBody" placeholder="Add a comment" style="flex:1; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:8px 10px;" />
          <button :disabled="adding || !commentBody.trim()" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:8px 10px; cursor:pointer;">{{ adding ? 'Sending…' : 'Send' }}</button>
        </form>
      </div>
    </div>
  </div>
</template>

