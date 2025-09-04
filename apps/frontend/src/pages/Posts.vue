<script setup>
import { ref, onMounted, onUnmounted, inject, onBeforeUnmount } from 'vue'
import { json } from '@/lib/http'
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import { useSessionStore } from '@/stores/session'
import { useUndo } from '@/composables/useUndo'
import UndoBar from '@/components/ui/UndoBar.vue'
import { PAGE_SIZE_POSTS } from '@/config/constants'
import ErrorCard from '@/components/ui/ErrorCard.vue'

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
const session = useSessionStore()
const { active: undoActive, label: undoLabel, remainingMs: undoMs, showUndo, cancel: undoCancel, dispose: undoDispose, confirm: undoConfirm } = useUndo()

async function fetchPosts(url = '/api/my-posts') {
  loading.value = true
  errorMsg.value = ''
  try {
    const payload = await json(url)
    const newResults = payload.results || []
    if (url === '/api/my-posts') results.value = newResults
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
    const tempId = Math.random()
    comments.value.unshift({ id: tempId, user: { username: 'You' }, body, created_at: new Date().toISOString() })
    const created = await json(`/api/posts/${activePost.value.id}/comments/`, { method: 'POST', body: JSON.stringify({ body }) })
    // Map tempId to real id
    const idx = comments.value.findIndex(c => c.id === tempId)
    if (idx !== -1) comments.value[idx].id = created.id
    showUndo('Comment posted — Undo?', async () => {
      // revert by deleting the created comment
      const idToDelete = created?.id ?? tempId
      try { await json(`/api/posts/${activePost.value.id}/comments/${idToDelete}/`, { method: 'DELETE' }) } catch {}
      const i = comments.value.findIndex(c => c.id === idToDelete)
      if (i !== -1) comments.value.splice(i, 1)
    })
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
    showUndo(likedBefore ? 'Like removed — Undo?' : 'Like added — Undo?', async () => {
      // revert the like back to original
      const revertMethod = likedBefore ? 'POST' : 'DELETE'
      post.likes_count = (post.likes_count || 0) - delta
      post._liked = likedBefore
      try { await json(`/api/posts/${post.id}/like/`, { method: revertMethod }) } catch {}
    })
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
  const remainingSlots = 4 - newPostPhotos.value.length

  if (files.length > remainingSlots) {
    showNotification(`You can only add up to 4 photos. ${remainingSlots} slots remaining.`, 'warning', 4000)
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
  if (!newPostBody.value.trim()) return
  creating.value = true
  try {
    const payload = {
      title: newPostTitle.value.trim() || null,
      body: newPostBody.value.trim(),
      is_published: true,
      visibility: 'public'
    }

    // Optimistic update
    const tempId = Math.random()
    const optimisticPost = {
      id: tempId,
      title: payload.title,
      body: payload.body,
      user: { id: session.user.id, username: session.user.username },
      is_published: true,
      visibility: 'public',
      likes_count: 0,
      comments_count: 0,
      created_at: new Date().toISOString(),
      _liked: false
    }
    results.value.unshift(optimisticPost)

    const post = await json('/api/posts/', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
    
    // Replace optimistic post with real one
    const index = results.value.findIndex(p => p.id === tempId)
    if (index !== -1) {
      results.value[index] = post
    }
    
    clearNewPost()
    createModalOpen.value = false
    
    // Show Undo option
    showUndo('Post created — Undo?', async () => {
      try {
        await json(`/api/posts/${post.id}/`, { method: 'DELETE' })
        const postIndex = results.value.findIndex(p => p.id === post.id)
        if (postIndex !== -1) {
          results.value.splice(postIndex, 1)
        }
      } catch (e) {
        console.error('Failed to delete post:', e)
      }
    })
  } catch (e) {
    // Remove optimistic post on error
    const index = results.value.findIndex(p => p.id === tempId)
    if (index !== -1) {
      results.value.splice(index, 1)
    }
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
    showNotification('Post updated successfully!', 'success', 3000)
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

onBeforeUnmount(() => {
  undoDispose()
})
</script>

<template>
  <div class="container">
    <Breadcrumbs />

    <div style="display:flex; align-items:center; gap:8px; margin:0 0 16px;">
      <h2 style="margin:0; font-size:22px; font-weight:700;">Posts <span style="font-size:14px; color:var(--c-text-muted);">(Page size: {{ PAGE_SIZE_POSTS }})</span></h2>
      <div style="margin-left:auto; display:flex; align-items:center; gap:12px;">
        <button @click="createModalOpen = true" style="border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:10px; padding:8px 16px; cursor:pointer; font-size:13px; font-weight:500;">Create Post</button>
        <button @click="fetchPosts()" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:8px 12px; cursor:pointer; font-size:13px;">Refresh</button>
      </div>
    </div>

    <div v-if="loading" class="grid grid-cols-responsive" style="gap:12px;">
      <div v-for="i in 6" :key="i" class="card" style="padding:16px; display:grid; gap:12px;">
        <div style="display:flex; align-items:center; gap:8px;">
          <div style="width:32px; height:32px; border-radius:50%; background:#e5e7eb;"></div>
          <div style="flex:1;">
            <div style="height:10px; width:100px; background:#e5e7eb; border-radius:6px; margin-bottom:6px;"></div>
            <div style="height:10px; width:80px; background:#e5e7eb; border-radius:6px;"></div>
          </div>
        </div>
        <div>
          <div style="height:14px; width:60%; background:#e5e7eb; border-radius:6px; margin-bottom:8px;"></div>
          <div style="height:12px; width:100%; background:#e5e7eb; border-radius:6px;"></div>
        </div>
      </div>
    </div>
    <ErrorCard
      v-else-if="errorMsg"
      title="Couldn't load posts"
      :message="errorMsg"
      :showRetry="true"
      @retry="fetchPosts"
    />
    <div v-else-if="results.length === 0" class="card" style="padding:32px; text-align:center; color:var(--c-text-muted);">
      <div style="font-size:48px; margin-bottom:16px;">📝</div>
      <div style="font-size:18px; font-weight:600; margin-bottom:8px;">No posts yet</div>
      <div>Create your first post to get started!</div>
    </div>
    <div v-else class="grid grid-cols-responsive" style="gap:12px;">
      <div v-for="p in results" :key="p.id" class="card" style="padding:16px; display:grid; gap:12px;">
        <div style="display:flex; align-items:center; gap:8px;">
          <div style="width:32px; height:32px; border-radius:50%; background:linear-gradient(135deg,#ff4db0,#4db2ff); display:grid; place-items:center; color:#fff; font-weight:600; font-size:12px;">
            {{ (p.user?.username || 'U').charAt(0).toUpperCase() }}
          </div>
          <div style="min-width:0;">
            <div style="font-weight:600; font-size:14px;">{{ p.user?.username || 'User' }}</div>
            <div style="color:var(--c-text-muted); font-size:12px;">{{ formatDate(p.created_at) }}</div>
          </div>
        </div>

        <div>
          <div style="font-weight:700; font-size:16px; margin-bottom:8px;">{{ p.title }}</div>
          <div style="color:var(--c-text-muted); font-size:14px; line-height:1.5;">{{ p.body?.slice(0, 140) }}{{ p.body?.length > 140 ? '...' : '' }}</div>
        </div>

        <div style="display:flex; gap:10px; align-items:center; font-size:13px; color:var(--c-text-muted);">
          <span>❤ {{ p.likes_count || 0 }}</span>
          <span>💬 {{ p.comments_count || 0 }}</span>
          <button :disabled="p._liking" @click="toggleLike(p)" style="margin-left:auto; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:4px 8px; cursor:pointer; font-size:12px; transition: all 0.2s ease;">
            {{ p._liking ? '...' : (p._liked ? '❤️ Unlike' : '🤍 Like') }}
          </button>
          <button @click="openPost(p)" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:4px 8px; cursor:pointer; font-size:12px;">Details</button>
          <button v-if="p.user?.username === session.user?.username" @click="editPost(p)" style="border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:10px; padding:4px 8px; cursor:pointer; font-size:12px;">✏️ Edit</button>
        </div>
      </div>
    </div>

    <div style="display:flex; justify-content:center; margin-top:12px;">
      <button v-if="next" @click="loadMore" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:8px 16px; cursor:pointer; font-size:13px;">Load more</button>
    </div>

    <!-- Create Post Modal -->
    <div v-if="createModalOpen" style="position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; padding:20px; z-index:1000;">
      <div class="card" style="width:100%; max-width:600px; background:var(--c-bg); color:var(--c-text); border:1px solid var(--c-border); border-radius:16px; padding:24px;">
        <div style="display:flex; align-items:center; margin-bottom:20px;">
          <div style="font-weight:700; font-size:20px;">Create New Post</div>
          <button @click="createModalOpen=false" style="margin-left:auto; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:8px 12px; cursor:pointer; font-size:12px;">Close</button>
        </div>

        <form @submit.prevent="createPost" style="display:grid; gap:16px;">
          <div>
            <label style="display:block; font-weight:600; margin-bottom:8px; color:var(--c-text);">Title</label>
            <input v-model="newPostTitle" placeholder="Enter post title" required style="width:100%; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:12px; font-size:14px;" />
          </div>

          <div>
            <label style="display:block; font-weight:600; margin-bottom:8px; color:var(--c-text);">Content</label>
            <textarea v-model="newPostBody" placeholder="Write your post content..." required rows="6" style="width:100%; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:12px; font-size:14px; resize:vertical;"></textarea>
          </div>

          <!-- Photo Upload Section -->
          <div>
            <label style="display:block; font-weight:600; margin-bottom:8px; color:var(--c-text);">
              Photos (Optional - Max 4)
            </label>

            <!-- Photo Upload Button -->
            <div v-if="newPostPhotos.length < 4" style="margin-bottom: 12px;">
              <input
                type="file"
                multiple
                accept="image/*"
                @change="addPhoto"
                style="display: none;"
                :id="'photo-upload-' + Date.now()"
              />
              <label
                :for="'photo-upload-' + Date.now()"
                style="display: inline-flex; align-items: center; gap: 8px; border: 2px dashed var(--c-border); border-radius: 10px; padding: 16px; cursor: pointer; transition: all 0.2s ease; background: var(--c-surface-2);"
                @mouseenter="$event.target.style.borderColor = 'var(--c-accent)'"
                @mouseleave="$event.target.style.borderColor = 'var(--c-border)'"
              >
                📸 <span style="font-weight: 500;">Add Photos</span>
                <span style="font-size: 12px; color: var(--c-text-muted);">({{ 4 - newPostPhotos.length }} slots left)</span>
              </label>
            </div>

            <!-- Photo Previews -->
            <div v-if="newPostPhotos.length > 0" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; margin-bottom: 12px;">
              <div
                v-for="(photo, index) in newPostPhotos"
                :key="index"
                style="position: relative; border-radius: 10px; overflow: hidden; border: 1px solid var(--c-border);"
              >
                <img
                  :src="photo.preview"
                  :alt="photo.name"
                  style="width: 100%; height: 120px; object-fit: cover; display: block;"
                />
                <button
                  @click="removePhoto(index)"
                  type="button"
                  style="position: absolute; top: 4px; right: 4px; width: 24px; height: 24px; border-radius: 50%; background: rgba(0, 0, 0, 0.7); color: white; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 14px;"
                >
                  ×
                </button>
                <div style="position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0, 0, 0, 0.7); color: white; padding: 4px 8px; font-size: 10px; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                  {{ photo.name }}
                </div>
              </div>
            </div>
          </div>

          <div style="display:flex; gap:12px; justify-content:flex-end;">
            <button type="button" @click="createModalOpen=false" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 20px; cursor:pointer; font-size:14px;">Cancel</button>
            <button type="submit" :disabled="creating || !newPostTitle.trim() || !newPostBody.trim()" style="border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:10px; padding:10px 20px; cursor:pointer; font-size:14px; font-weight:500;">
              {{ creating ? 'Creating...' : 'Create Post' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Post Modal -->
    <div v-if="editModalOpen" style="position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; padding:20px; z-index:1000;">
      <div class="card" style="width:100%; max-width:600px; background:var(--c-bg); color:var(--c-text); border:1px solid var(--c-border); border-radius:16px; padding:24px;">
        <div style="display:flex; align-items:center; margin-bottom:20px;">
          <div style="font-weight:700; font-size:20px;">Edit Post</div>
          <button @click="editModalOpen=false" style="margin-left:auto; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:8px 12px; cursor:pointer; font-size:12px;">Close</button>
        </div>

        <form @submit.prevent="saveEdit" style="display:grid; gap:16px;">
          <div>
            <label style="display:block; font-weight:600; margin-bottom:8px; color:var(--c-text);">Title</label>
            <input v-model="editTitle" placeholder="Enter post title" required style="width:100%; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:12px; font-size:14px;" />
          </div>

          <div>
            <label style="display:block; font-weight:600; margin-bottom:8px; color:var(--c-text);">Content</label>
            <textarea v-model="editBody" placeholder="Write your post content..." required rows="6" style="width:100%; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:12px; font-size:14px; resize:vertical;"></textarea>
          </div>

          <div style="display:flex; gap:12px; justify-content:flex-end;">
            <button type="button" @click="editModalOpen=false" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 20px; cursor:pointer; font-size:14px;">Cancel</button>
            <button type="submit" :disabled="editing || !editTitle.trim() || !editBody.trim()" style="border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:10px; padding:10px 20px; cursor:pointer; font-size:14px; font-weight:500;">
              {{ editing ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Post Detail Modal -->
    <div v-if="modalOpen" style="position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; padding:20px; z-index:1000;">
      <div class="card" style="width:100%; max-width:720px; background:var(--c-bg); color:var(--c-text); border:1px solid var(--c-border); border-radius:16px; padding:24px;">
        <div style="display:flex; align-items:center; margin-bottom:16px;">
          <div style="font-weight:700; font-size:20px;">{{ activePost?.title }}</div>
          <button @click="modalOpen=false" style="margin-left:auto; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:8px 12px; cursor:pointer; font-size:12px;">Close</button>
        </div>

        <div style="margin-bottom:16px; font-size:14px; color:var(--c-text-muted);">
          By {{ activePost?.user?.username || 'User' }} • {{ formatDate(activePost?.created_at) }}
        </div>

        <div style="margin-bottom:20px; font-size:16px; color:var(--c-text); line-height:1.6; white-space:pre-wrap;">{{ activePost?.body }}</div>

        <div style="margin-bottom:16px; font-weight:700; font-size:16px;">Comments</div>
        <div v-if="comments.length===0" style="color:var(--c-text-muted); font-size:14px; text-align:center; padding:20px;">No comments yet. Be the first to comment!</div>
        <ul style="list-style:none; padding:0; margin:16px 0; display:grid; gap:12px;">
          <li v-for="c in comments" :key="c.id" class="card" style="padding:16px;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
              <div style="width:24px; height:24px; border-radius:50%; background:linear-gradient(135deg,#ff4db0,#4db2ff); display:grid; place-items:center; color:#fff; font-weight:600; font-size:10px;">
                {{ (c.user?.username || 'U').charAt(0).toUpperCase() }}
              </div>
              <div style="font-weight:600; font-size:13px; color:var(--c-text);">{{ c.user?.username || 'User' }}</div>
              <div style="color:var(--c-text-muted); font-size:11px;">{{ formatDate(c.created_at) }}</div>
            </div>
            <div style="font-size:14px; color:var(--c-text); line-height:1.5;">{{ c.body }}</div>
          </li>
        </ul>

        <form @submit.prevent="addComment" style="display:flex; gap:12px; margin-top:20px;">
          <input v-model="commentBody" placeholder="Add a comment..." required style="flex:1; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:12px; font-size:14px;" />
          <button :disabled="adding || !commentBody.trim()" style="border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:10px; padding:12px 20px; cursor:pointer; font-size:14px; font-weight:500;">
            {{ adding ? 'Sending…' : 'Send' }}
          </button>
        </form>
      </div>
    </div>
  </div>

  <UndoBar v-if="undoActive" :label="undoLabel" :ttlMs="undoMs" @confirm="undoConfirm" @cancel="undoCancel" />
</template>
