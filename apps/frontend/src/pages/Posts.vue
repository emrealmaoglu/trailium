<script setup>
import { ref, onMounted, onUnmounted, inject } from 'vue'
import { json } from '@/lib/http'
import Breadcrumbs from '@/components/Breadcrumbs.vue'

// Constants - no more magic numbers
const MAX_POST_TITLE_LENGTH = 100
const MAX_POST_BODY_LENGTH = 1000
const MAX_PHOTOS_PER_POST = 4
const DEFAULT_PAGE_SIZE = 20

const loading = ref(true)
const errorMsg = ref('')
const results = ref([])
const next = ref(null)
const modalOpen = ref(false)
const activePost = ref(null)
const comments = ref([])
const adding = ref(false)
const commentBody = ref('')
const createModalOpen = ref(false)
const newPostTitle = ref('')
const newPostBody = ref('')
const creating = ref(false)
const newPostPhotos = ref([])
const editModalOpen = ref(false)
const editTitle = ref('')
const editBody = ref('')
const editing = ref(false)
const editingPost = ref(null)

const showNotification = inject('showNotification')

async function fetchPosts(url = '/api/posts/') {
  loading.value = true
  errorMsg.value = ''
  try {
    const payload = await json(url)
    const newResults = payload.results || []
    if (url === '/api/posts/') results.value = newResults
    else results.value = results.value.concat(newResults)
    next.value = payload.next || ''
  } catch (e) {
    errorMsg.value = 'Could not load posts.'
    showNotification('Failed to load posts', 'error', 5000)
  } finally {
    loading.value = false
  }
}

function loadMore() {
  if (next.value) fetchPosts(next.value)
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
    showNotification('Failed to add comment', 'error', 5000)
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
    showNotification('Failed to update like', 'error', 3000)
  } finally {
    post._liking = false
  }
}

// Photo handling
function addPhoto(event) {
  const files = Array.from(event.target.files)
  const remainingSlots = MAX_PHOTOS_PER_POST - newPostPhotos.value.length

  if (files.length > remainingSlots) {
    showNotification(`You can only add up to ${MAX_PHOTOS_PER_POST} photos. ${remainingSlots} slots remaining.`, 'warning', 4000)
    return
  }

  files.forEach(file => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        newPostPhotos.value.push({
          file: file,
          preview: e.target.result,
          name: file.name
        })
      }
      reader.readAsDataURL(file)
    } else {
      showNotification(`${file.name} is not an image file.`, 'error', 3000)
    }
  })
}

function removePhoto(index) {
  newPostPhotos.value.splice(index, 1)
}

function clearNewPost() {
  newPostTitle.value = ''
  newPostBody.value = ''
  newPostPhotos.value = []
}

async function createPost() {
  if (!newPostTitle.value.trim() || !newPostBody.value.trim()) return
  creating.value = true
  try {
    const formData = new FormData()
    formData.append('title', newPostTitle.value)
    formData.append('body', newPostBody.value)

    // Add photos if any
    newPostPhotos.value.forEach((photo, index) => {
      formData.append(`photos`, photo.file)
    })

    const post = await json('/api/posts/', {
      method: 'POST',
      body: formData
    })
    results.value.unshift(post)
          clearNewPost()
      createModalOpen.value = false
  } catch (e) {
    errorMsg.value = 'Could not create post.'
    showNotification('Failed to create post', 'error', 5000)
  } finally {
    creating.value = false
  }
}

async function saveEdit() {
  if (!editTitle.value.trim() || !editBody.value.trim()) return
  editing.value = true
  try {
    const updatedPost = await json(`/api/posts/${editingPost.value.id}/`, {
      method: 'PATCH',
      body: JSON.stringify({
        title: editTitle.value,
        body: editBody.value
      })
    })

    // Update the post in the results
    const index = results.value.findIndex(p => p.id === editingPost.value.id)
    if (index !== -1) {
      results.value[index] = { ...results.value[index], ...updatedPost }
    }

          editModalOpen.value = false
      editingPost.value = null
  } catch (e) {
    showNotification('Failed to update post', 'error', 5000)
  } finally {
    editing.value = false
  }
}

function editPost(post) {
  editingPost.value = post
  editTitle.value = post.title
  editBody.value = post.body
  editModalOpen.value = true
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
  fetchPosts()
  const onVis = () => { if (document.visibilityState === 'visible') fetchPosts() }
  document.addEventListener('visibilitychange', onVis)
  onUnmounted(() => document.removeEventListener('visibilitychange', onVis))
})
</script>

<template>
  <div class="posts-page">
    <div class="posts-header">
      <h1 class="posts-title">Posts</h1>
      <button @click="createModalOpen = true" class="create-post-btn">
        <span class="btn-icon">✏️</span>
        Create Post
      </button>
    </div>

    <div v-if="errorMsg" class="error-message">{{ errorMsg }}</div>

    <!-- Create Post Modal -->
    <div v-if="createModalOpen" class="modal-overlay" @click="createModalOpen = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Create New Post</h2>
          <button @click="createModalOpen = false" class="close-btn">×</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label for="post-title">Title</label>
            <input
              id="post-title"
              v-model="newPostTitle"
              type="text"
              placeholder="Post title..."
              class="form-input"
              :maxlength="MAX_POST_TITLE_LENGTH"
            />
          </div>

          <div class="form-group">
            <label for="post-body">Content</label>
            <textarea
              id="post-body"
              v-model="newPostBody"
              placeholder="What's on your mind?"
              class="form-textarea"
              rows="4"
              :maxlength="MAX_POST_BODY_LENGTH"
            ></textarea>
          </div>

          <div class="form-group">
            <label>Photos (up to {{ MAX_PHOTOS_PER_POST }})</label>
            <div class="photo-upload">
              <input
                type="file"
                multiple
                accept="image/*"
                @change="addPhoto"
                class="photo-input"
                :disabled="newPostPhotos.length >= MAX_PHOTOS_PER_POST"
              />
              <div class="photo-preview">
                <div
                  v-for="(photo, index) in newPostPhotos"
                  :key="index"
                  class="photo-item"
                >
                  <img :src="photo.preview" :alt="photo.name" class="photo-img" />
                  <button @click="removePhoto(index)" class="remove-photo-btn">×</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="createModalOpen = false" class="cancel-btn">Cancel</button>
          <button
            @click="createPost"
            :disabled="creating || !newPostTitle.trim() || !newPostBody.trim()"
            class="submit-btn"
          >
            {{ creating ? 'Creating...' : 'Create Post' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Posts Grid -->
    <div class="posts-grid">
      <div v-for="post in results" :key="post.id" class="post-card">
        <div class="post-header">
          <div class="user-info">
            <div class="user-avatar">
              {{ (post.user?.username || 'U').charAt(0).toUpperCase() }}
            </div>
            <div class="user-details">
              <div class="username">{{ post.user?.username || 'User' }}</div>
              <div class="post-date">{{ formatDate(post.created_at) }}</div>
            </div>
          </div>
          <div class="post-actions">
            <button @click="toggleLike(post)" :disabled="post._liking" class="like-btn">
              <span v-if="post._liking">...</span>
              <span v-else-if="post._liked">❤️</span>
              <span v-else>🤍</span>
            </button>
            <button @click="openPost(post)" class="comment-btn">
              💬 {{ post.comments_count || 0 }}
            </button>
          </div>
        </div>

        <div class="post-content">
          <h3 class="post-title">{{ post.title }}</h3>
          <p class="post-body">{{ post.body }}</p>

          <div v-if="post.photos && post.photos.length > 0" class="post-photos">
            <div class="photos-grid" :class="`photos-${post.photos.length}`">
              <img
                v-for="photo in post.photos"
                :key="photo.id"
                :src="photo.url"
                :alt="photo.caption || 'Post photo'"
                class="post-photo"
                @click="openPhotoViewer(photo)"
              />
            </div>
          </div>
        </div>

        <div class="post-stats">
          <span class="stat-item">
            <span class="stat-icon">❤️</span>
            {{ post.likes_count || 0 }}
          </span>
          <span class="stat-item">
            <span class="stat-icon">💬</span>
            {{ post.comments_count || 0 }}
          </span>
        </div>
      </div>
    </div>

    <!-- Comments Modal -->
    <div v-if="modalOpen" class="modal-overlay" @click="modalOpen = false">
      <div class="modal-content comments-modal" @click.stop>
        <div class="modal-header">
          <h2>{{ activePost?.title }}</h2>
          <button @click="modalOpen = false" class="close-btn">×</button>
        </div>

        <div class="modal-body">
          <div class="post-detail">
            <div class="post-meta">
              By {{ activePost?.user?.username || 'User' }} • {{ formatDate(activePost?.created_at) }}
            </div>
            <p class="post-detail-body">{{ activePost?.body }}</p>
          </div>

          <div class="comments-section">
            <h3>Comments</h3>
            <div v-if="comments.length === 0" class="no-comments">
              No comments yet. Be the first to comment!
            </div>
            <div v-else class="comments-list">
              <div v-for="c in comments" :key="c.id" class="comment-item">
                <div class="comment-header">
                  <div class="comment-avatar">
                    {{ (c.user?.username || 'U').charAt(0).toUpperCase() }}
                  </div>
                  <div class="comment-info">
                    <div class="comment-user">{{ c.user?.username || 'User' }}</div>
                    <div class="comment-date">{{ formatDate(c.created_at) }}</div>
                  </div>
                </div>
                <div class="comment-body">{{ c.body }}</div>
              </div>
            </div>
          </div>

          <div class="add-comment">
            <textarea
              v-model="commentBody"
              placeholder="Add a comment..."
              class="comment-input"
              rows="3"
              required
            ></textarea>
            <button
              @click="addComment"
              :disabled="adding || !commentBody.trim()"
              class="comment-submit-btn"
            >
              {{ adding ? 'Sending…' : 'Send' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Post Modal -->
    <div v-if="editModalOpen" class="modal-overlay" @click="editModalOpen = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Edit Post</h2>
          <button @click="editModalOpen = false" class="close-btn">×</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label for="edit-title">Title</label>
            <input
              id="edit-title"
              v-model="editTitle"
              placeholder="Enter post title"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="edit-body">Content</label>
            <textarea
              id="edit-body"
              v-model="editBody"
              placeholder="Write your post content..."
              required
              rows="6"
              class="form-textarea"
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="editModalOpen = false" class="cancel-btn">Cancel</button>
          <button
            @click="saveEdit"
            :disabled="editing || !editTitle.trim() || !editBody.trim()"
            class="submit-btn"
          >
            {{ editing ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-icon">⏳</div>
      <p>Loading posts...</p>
    </div>

    <!-- Empty State -->
    <div v-if="results.length === 0 && !loading" class="empty-state">
      <div class="empty-icon">📝</div>
      <h3>No posts yet</h3>
      <p>Be the first to share something!</p>
      <button @click="createModalOpen = true" class="create-first-post-btn">
        Create Your First Post
      </button>
    </div>
  </div>
</template>

<style scoped>
.posts-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 16px;
}

.posts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  gap: 20px;
}

.posts-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0;
  color: var(--c-text);
}

.create-post-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--c-accent);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px 20px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.create-post-btn:hover {
  background: var(--c-accent-dark, #7c3aed);
  transform: translateY(-1px);
}

.btn-icon {
  font-size: 18px;
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

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: var(--c-surface);
  border-radius: 16px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 16px;
  border-bottom: 1px solid var(--c-border);
}

.modal-header h2 {
  margin: 0;
  font-size: 24px;
  color: var(--c-text);
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  color: var(--c-text-muted);
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: var(--c-surface-2);
  color: var(--c-text);
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--c-text);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid var(--c-border);
  border-radius: 8px;
  font-size: 16px;
  background: var(--c-surface);
  color: var(--c-text);
  transition: border-color 0.2s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--c-accent);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.photo-upload {
  border: 2px dashed var(--c-border);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.photo-input {
  margin-bottom: 16px;
}

.photo-preview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 12px;
  max-width: 300px;
  margin: 0 auto;
}

.photo-item {
  position: relative;
  aspect-ratio: 1;
}

.photo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.remove-photo-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 16px 24px 24px;
  border-top: 1px solid var(--c-border);
}

.cancel-btn {
  background: var(--c-surface);
  color: var(--c-text);
  border: 2px solid var(--c-border);
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background: var(--c-surface-2);
  border-color: var(--c-accent);
}

.submit-btn {
  background: var(--c-accent);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.submit-btn:hover:not(:disabled) {
  background: var(--c-accent-dark, #7c3aed);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Posts Grid */
.posts-grid {
  display: grid;
  gap: 24px;
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
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
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

.user-details {
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

.post-actions {
  display: flex;
  gap: 8px;
}

.like-btn,
.comment-btn {
  background: var(--c-surface);
  color: var(--c-text);
  border: 2px solid var(--c-border);
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
  min-width: 60px;
}

.like-btn:hover,
.comment-btn:hover {
  background: var(--c-accent);
  color: white;
  border-color: var(--c-accent);
}

.like-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  margin: 0 0 16px 0;
}

.post-photos {
  margin-top: 16px;
}

.photos-grid {
  display: grid;
  gap: 8px;
  border-radius: 12px;
  overflow: hidden;
}

.photos-1 {
  grid-template-columns: 1fr;
}

.photos-2 {
  grid-template-columns: 1fr 1fr;
}

.photos-3,
.photos-4 {
  grid-template-columns: 1fr 1fr;
}

.post-photo {
  width: 100%;
  height: 200px;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.post-photo:hover {
  transform: scale(1.02);
}

.post-stats {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: var(--c-text-muted);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.stat-icon {
  font-size: 16px;
}

/* Comments Modal */
.comments-modal {
  max-width: 500px;
}

.post-detail {
  margin-bottom: 24px;
}

.post-meta {
  font-size: 14px;
  color: var(--c-text-muted);
  margin-bottom: 12px;
}

.post-detail-body {
  font-size: 16px;
  color: var(--c-text);
  line-height: 1.6;
  white-space: pre-wrap;
  margin: 0;
}

.comments-section {
  margin-bottom: 24px;
}

.comments-section h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: var(--c-text);
}

.no-comments {
  color: var(--c-text-muted);
  font-size: 14px;
  text-align: center;
  padding: 20px;
}

.comments-list {
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
}

.comment-item {
  padding: 16px;
  border: 1px solid var(--c-border);
  border-radius: 8px;
  background: var(--c-surface-2);
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.comment-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff4db0, #4db2ff);
  display: grid;
  place-items: center;
  color: white;
  font-weight: 600;
  font-size: 10px;
  flex-shrink: 0;
}

.comment-info {
  min-width: 0;
}

.comment-user {
  font-weight: 600;
  font-size: 13px;
  color: var(--c-text);
  margin-bottom: 2px;
}

.comment-date {
  color: var(--c-text-muted);
  font-size: 11px;
}

.comment-body {
  font-size: 14px;
  color: var(--c-text);
  line-height: 1.5;
}

.add-comment {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-input {
  width: 100%;
  padding: 12px;
  border: 2px solid var(--c-border);
  border-radius: 8px;
  font-size: 16px;
  background: var(--c-surface);
  color: var(--c-text);
  resize: vertical;
  min-height: 80px;
}

.comment-input:focus {
  outline: none;
  border-color: var(--c-accent);
}

.comment-submit-btn {
  background: var(--c-accent);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  align-self: flex-end;
}

.comment-submit-btn:hover:not(:disabled) {
  background: var(--c-accent-dark, #7c3aed);
}

.comment-submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Loading and Empty States */
.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--c-text-muted);
}

.loading-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--c-text);
}

.empty-state p {
  margin: 0 0 24px 0;
  font-size: 16px;
}

.create-first-post-btn {
  background: var(--c-accent);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.create-first-post-btn:hover {
  background: var(--c-accent-dark, #7c3aed);
  transform: translateY(-1px);
}

/* Responsive Design */
@media (max-width: 768px) {
  .posts-page {
    padding: 0 12px;
  }

  .posts-header {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }

  .posts-title {
    font-size: 28px;
  }

  .create-post-btn {
    align-self: center;
    max-width: 200px;
  }

  .modal-overlay {
    padding: 12px;
  }

  .modal-content {
    max-height: 95vh;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 20px;
  }

  .post-card {
    padding: 20px;
  }

  .post-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .post-actions {
    justify-content: center;
  }

  .post-title {
    font-size: 18px;
  }

  .post-body {
    font-size: 15px;
  }

  .photos-3,
  .photos-4 {
    grid-template-columns: 1fr;
  }

  .post-photo {
    height: 150px;
  }
}

@media (max-width: 480px) {
  .posts-page {
    padding: 0 8px;
  }

  .posts-title {
    font-size: 24px;
  }

  .post-card {
    padding: 16px;
  }

  .post-title {
    font-size: 16px;
  }

  .post-body {
    font-size: 14px;
  }

  .user-avatar {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }

  .like-btn,
  .comment-btn {
    padding: 6px 10px;
    font-size: 13px;
    min-width: 50px;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 16px;
  }

  .modal-header h2 {
    font-size: 20px;
  }

  .form-input,
  .form-textarea,
  .comment-input {
    padding: 10px;
    font-size: 15px;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .post-card,
  .modal-content {
    border-width: 2px;
  }

  .form-input,
  .form-textarea,
  .comment-input {
    border-width: 2px;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .post-card,
  .create-post-btn,
  .like-btn,
  .comment-btn,
  .post-photo {
    transition: none;
  }

  .post-card:hover {
    transform: none;
  }

  .create-post-btn:hover,
  .like-btn:hover,
  .comment-btn:hover {
    transform: none;
  }

  .post-photo:hover {
    transform: none;
  }
}
</style>
