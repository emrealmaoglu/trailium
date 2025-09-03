<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { json } from '@/lib/http'

const loading = ref(true)
const errorMsg = ref('')
const results = ref([])
const next = ref('')
const sentinel = ref(null)
let observer

async function fetchFeed(url = '/api/feed/posts') {
  loading.value = true
  errorMsg.value = ''
  try {
    const payload = await json(url)
    results.value = results.value.concat(payload.results || [])
    next.value = payload.next || ''
  } catch {
    errorMsg.value = 'Could not load feed.'
  } finally {
    loading.value = false
  }
}

function onIntersect(entries) {
  const [entry] = entries
  if (entry.isIntersecting && next.value && !loading.value) {
    fetchFeed(next.value)
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

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchFeed()
  observer = new IntersectionObserver(onIntersect, { rootMargin: '200px' })
  if (sentinel.value) observer.observe(sentinel.value)
})

onUnmounted(() => {
  if (observer && sentinel.value) observer.unobserve(sentinel.value)
})
</script>

<template>
  <div class="container">
    <div style="display:flex; align-items:center; gap:8px; margin:0 0 16px;">
      <h2 style="margin:0; font-size:22px; font-weight:700;">Your Feed</h2>
      <div style="margin-left:auto; display:flex; align-items:center; gap:12px; color:var(--c-text-muted); font-size:13px;">
        <span>Page size: 5</span>
        <button @click="fetchFeed()" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:8px 12px; cursor:pointer; font-size:13px;">Refresh</button>
      </div>
    </div>

    <div v-if="errorMsg" class="card" style="padding:16px; color:var(--c-text-muted); display:flex; align-items:center; gap:12px;">
      <span style="flex:1;">{{ errorMsg }}</span>
      <button @click="fetchFeed()" style="border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:10px; padding:8px 12px; cursor:pointer; font-size:13px;">Retry</button>
    </div>

    <div v-if="results.length === 0 && !loading" class="card" style="padding:32px; text-align:center; color:var(--c-text-muted);">
      <div style="font-size:48px; margin-bottom:16px;">📰</div>
      <div style="font-size:18px; font-weight:600; margin-bottom:8px;">No posts in your feed</div>
      <div>Follow some users to see their posts here!</div>
    </div>

    <div v-if="loading" class="grid grid-cols-responsive" style="gap:16px;">
      <div v-for="i in 6" :key="i" class="card" style="padding:20px; display:grid; gap:16px;">
        <div style="display:flex; align-items:center; gap:12px;">
          <div style="width:40px; height:40px; border-radius:50%; background:#e5e7eb;"></div>
          <div style="flex:1;">
            <div style="height:12px; width:120px; background:#e5e7eb; border-radius:6px; margin-bottom:6px;"></div>
            <div style="height:10px; width:80px; background:#e5e7eb; border-radius:6px;"></div>
          </div>
        </div>
        <div>
          <div style="height:16px; width:60%; background:#e5e7eb; border-radius:6px; margin-bottom:10px;"></div>
          <div style="height:12px; width:100%; background:#e5e7eb; border-radius:6px;"></div>
        </div>
        <div style="display:flex; gap:12px;">
          <div style="height:12px; width:60px; background:#e5e7eb; border-radius:6px;"></div>
          <div style="height:12px; width:60px; background:#e5e7eb; border-radius:6px;"></div>
        </div>
      </div>
    </div>

    <div v-else class="grid grid-cols-responsive" style="gap:16px;">
      <div v-for="p in results" :key="p.id" class="card" style="padding:20px; display:grid; gap:16px;">
        <!-- User Header -->
        <div style="display:flex; align-items:center; gap:12px;">
          <div style="width:40px; height:40px; border-radius:50%; background:linear-gradient(135deg,#ff4db0,#4db2ff); display:grid; place-items:center; color:#fff; font-weight:600; font-size:14px;">
            {{ (p.user?.username || 'U').charAt(0).toUpperCase() }}
          </div>
          <div style="min-width:0;">
            <div style="font-weight:600; font-size:15px; color:var(--c-text);">{{ p.user?.username || 'User' }}</div>
            <div style="color:var(--c-text-muted); font-size:12px;">{{ formatDate(p.created_at) }}</div>
          </div>
        </div>

        <!-- Post Content -->
        <div>
          <div style="font-weight:700; font-size:18px; margin-bottom:12px; color:var(--c-text);">{{ p.title }}</div>
          <div style="color:var(--c-text-muted); font-size:15px; line-height:1.6;">{{ p.body }}</div>
        </div>

        <!-- Post Stats and Actions -->
        <div style="display:flex; gap:12px; align-items:center; font-size:13px; color:var(--c-text-muted);">
          <span style="display:flex; align-items:center; gap:4px;">
            <span style="font-size:16px;">❤️</span>
            {{ p.likes_count || 0 }}
          </span>
          <span style="display:flex; align-items:center; gap:4px;">
            <span style="font-size:16px;">💬</span>
            {{ p.comments_count || 0 }}
          </span>
          <button :disabled="p._liking" @click="toggleLike(p)" style="margin-left:auto; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:6px 12px; cursor:pointer; font-size:12px; transition: all 0.2s ease;">
            <span v-if="p._liking">...</span>
            <span v-else-if="p._liked">❤️ Unlike</span>
            <span v-else>🤍 Like</span>
          </button>
        </div>
      </div>
    </div>

    <div ref="sentinel" style="height:1px;"></div>
  </div>
</template>
