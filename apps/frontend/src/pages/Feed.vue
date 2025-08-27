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
  <div class="feed-page">
            <div class="feed-header">
          <h2 class="feed-title">Your Feed</h2>
        </div>

    <div v-if="errorMsg" class="error-message">{{ errorMsg }}</div>

    <div v-if="results.length === 0 && !loading" class="empty-state">
      <div class="empty-icon">📰</div>
      <h3 class="empty-title">No posts in your feed</h3>
      <p class="empty-description">Follow some users to see their posts here!</p>
    </div>

    <div class="feed-grid">
      <div v-for="p in results" :key="p.id" class="post-card">
        <!-- User Header -->
        <div class="post-header">
          <div class="user-avatar">
            {{ (p.user?.username || 'U').charAt(0).toUpperCase() }}
          </div>
          <div class="user-info">
            <div class="username">{{ p.user?.username || 'User' }}</div>
            <div class="post-date">{{ formatDate(p.created_at) }}</div>
          </div>
        </div>

        <!-- Post Content -->
        <div class="post-content">
          <h3 class="post-title">{{ p.title }}</h3>
          <p class="post-body">{{ p.body }}</p>
        </div>

        <!-- Post Stats and Actions -->
        <div class="post-actions">
          <div class="post-stats">
            <span class="stat-item">
              <span class="stat-icon">❤️</span>
              {{ p.likes_count || 0 }}
            </span>
            <span class="stat-item">
              <span class="stat-icon">💬</span>
              {{ p.comments_count || 0 }}
            </span>
          </div>
          <button
            :disabled="p._liking"
            @click="toggleLike(p)"
            class="like-btn"
            :class="{ 'liked': p._liked, 'liking': p._liking }"
          >
            <span v-if="p._liking">...</span>
            <span v-else-if="p._liked">❤️ Unlike</span>
            <span v-else>🤍 Like</span>
          </button>
        </div>
      </div>
    </div>

    <div ref="sentinel" class="sentinel"></div>

    <div v-if="loading" class="loading-state">
      <div class="loading-icon">⏳</div>
      <p>Loading more posts...</p>
    </div>
  </div>
</template>

<style scoped>
.feed-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 16px;
}

.feed-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  gap: 16px;
}

.feed-title {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--c-text);
}

.refresh-btn {
  border: 2px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-text);
  border-radius: 12px;
  padding: 10px 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.refresh-btn:hover {
  background: var(--c-accent);
  color: white;
  border-color: var(--c-accent);
  transform: translateY(-1px);
}

.error-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 12px;
  padding: 16px;
  color: #dc2626;
  margin-bottom: 24px;
  text-align: center;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--c-text-muted);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--c-text);
}

.empty-description {
  margin: 0;
  font-size: 16px;
}

.feed-grid {
  display: grid;
  gap: 20px;
  margin-bottom: 32px;
}

.post-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 16px;
  padding: 24px;
  transition: all 0.2s ease;
}

.post-card:hover {
  border-color: var(--c-accent);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.post-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff4db0, #4db2ff);
  display: grid;
  place-items: center;
  color: white;
  font-weight: 600;
  font-size: 18px;
  flex-shrink: 0;
}

.user-info {
  min-width: 0;
}

.username {
  font-weight: 600;
  font-size: 16px;
  color: var(--c-text);
  margin-bottom: 4px;
}

.post-date {
  color: var(--c-text-muted);
  font-size: 13px;
}

.post-content {
  margin-bottom: 20px;
}

.post-title {
  font-weight: 700;
  font-size: 20px;
  margin: 0 0 12px 0;
  color: var(--c-text);
  line-height: 1.3;
}

.post-body {
  color: var(--c-text-muted);
  font-size: 16px;
  line-height: 1.6;
  margin: 0;
  word-wrap: break-word;
}

.post-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.post-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--c-text-muted);
}

.stat-icon {
  font-size: 16px;
}

.like-btn {
  border: 2px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-text);
  border-radius: 10px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
  white-space: nowrap;
  min-width: 80px;
}

.like-btn:hover:not(:disabled) {
  background: var(--c-accent);
  color: white;
  border-color: var(--c-accent);
  transform: translateY(-1px);
}

.like-btn.liked {
  background: #fecaca;
  border-color: #f87171;
  color: #dc2626;
}

.like-btn.liked:hover {
  background: #fca5a5;
  border-color: #ef4444;
}

.like-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.sentinel {
  height: 1px;
  margin: 20px 0;
}

.loading-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--c-text-muted);
}

.loading-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.loading-state p {
  margin: 0;
  font-size: 16px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .feed-page {
    padding: 0 12px;
  }

  .feed-header {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }

  .feed-title {
    font-size: 24px;
  }

  .refresh-btn {
    align-self: center;
    max-width: 200px;
  }

  .post-card {
    padding: 20px;
  }

  .post-header {
    gap: 12px;
  }

  .user-avatar {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }

  .post-title {
    font-size: 18px;
  }

  .post-body {
    font-size: 15px;
  }

  .post-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .post-stats {
    justify-content: center;
  }

  .like-btn {
    align-self: center;
    max-width: 200px;
  }
}

@media (max-width: 480px) {
  .feed-page {
    padding: 0 8px;
  }

  .post-card {
    padding: 16px;
  }

  .post-header {
    flex-direction: column;
    text-align: center;
    gap: 8px;
  }

  .post-title {
    font-size: 16px;
  }

  .post-body {
    font-size: 14px;
  }

  .stat-item {
    font-size: 13px;
  }

  .like-btn {
    font-size: 12px;
    padding: 6px 12px;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .post-card {
    border-width: 2px;
  }

  .like-btn {
    border-width: 2px;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .post-card,
  .refresh-btn,
  .like-btn {
    transition: none;
  }

  .post-card:hover {
    transform: none;
  }

  .refresh-btn:hover,
  .like-btn:hover:not(:disabled) {
    transform: none;
  }
}
</style>
