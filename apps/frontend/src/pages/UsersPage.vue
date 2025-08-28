<!-- apps/frontend/src/pages/UsersPage.vue -->
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { json } from '@/lib/http'

const route = useRoute()
const loading = ref(true)
const errorMsg = ref('')
const isPrivate = ref(false)
const privateMessage = ref('')
const posts = ref([])
const albums = ref([])

// Comments state
const openPostId = ref(null)
const openAlbumId = ref(null)
const postComments = ref([])
const albumComments = ref([])
const newPostComment = ref('')
const newAlbumComment = ref('')
const commenting = ref(false)
const liking = ref(false)

async function loadContent() {
  loading.value = true
  errorMsg.value = ''
  isPrivate.value = false
  privateMessage.value = ''
  posts.value = []
  albums.value = []

  try {
    const userId = route.params.id
    const payload = await json(`/api/users/${userId}/content`)
    if (payload.private) {
      isPrivate.value = true
      privateMessage.value = payload.message || 'Bu hesap gizlidir.'
    } else {
      posts.value = payload.posts || []
      albums.value = payload.albums || []
    }
  } catch (e) {
    errorMsg.value = 'İçerik yüklenemedi.'
  } finally {
    loading.value = false
  }
}

async function likePost(post) {
  if (liking.value) return
  liking.value = true
  const prev = post.likes_count || 0
  post.likes_count = prev + 1
  try {
    await json(`/api/posts/${post.id}/like/`, { method: 'POST' })
  } catch {
    post.likes_count = prev
  } finally {
    liking.value = false
  }
}

async function likeAlbum(album) {
  if (liking.value) return
  liking.value = true
  const prev = album.likes_count || 0
  album.likes_count = prev + 1
  try {
    await json(`/api/albums/${album.id}/like/`, { method: 'POST' })
  } catch {
    album.likes_count = prev
  } finally {
    liking.value = false
  }
}

async function openPostComments(post) {
  if (openPostId.value === post.id) {
    openPostId.value = null
    postComments.value = []
    return
  }
  openPostId.value = post.id
  postComments.value = []
  try {
    postComments.value = await json(`/api/posts/${post.id}/comments/`)
  } catch {
    postComments.value = []
  }
}

async function openAlbumComments(album) {
  if (openAlbumId.value === album.id) {
    openAlbumId.value = null
    albumComments.value = []
    return
  }
  openAlbumId.value = album.id
  albumComments.value = []
  try {
    albumComments.value = await json(`/api/albums/${album.id}/comments/`)
  } catch {
    albumComments.value = []
  }
}

async function addPostComment() {
  if (!openPostId.value || !newPostComment.value.trim() || commenting.value) return
  commenting.value = true
  const body = newPostComment.value
  newPostComment.value = ''
  try {
    await json(`/api/posts/${openPostId.value}/comments/`, {
      method: 'POST',
      body: JSON.stringify({ body })
    })
    postComments.value.unshift({ id: Math.random(), user: { username: 'You' }, body, created_at: new Date().toISOString() })
  } finally {
    commenting.value = false
  }
}

async function addAlbumComment() {
  if (!openAlbumId.value || !newAlbumComment.value.trim() || commenting.value) return
  commenting.value = true
  const body = newAlbumComment.value
  newAlbumComment.value = ''
  try {
    await json(`/api/albums/${openAlbumId.value}/comments/`, {
      method: 'POST',
      body: JSON.stringify({ body })
    })
    albumComments.value.unshift({ id: Math.random(), user: { username: 'You' }, body, created_at: new Date().toISOString() })
  } finally {
    commenting.value = false
  }
}

onMounted(loadContent)
</script>

<template>
  <section class="max-w-5xl mx-auto py-6">
    <h1 class="text-2xl font-semibold">User Content</h1>

    <div v-if="loading" class="mt-4 rounded-2xl border border-white/10 p-6">Loading…</div>
    <div v-else-if="errorMsg" class="mt-4 rounded-2xl border border-white/10 p-6 text-white/70">{{ errorMsg }}</div>

    <div v-else>
      <div v-if="isPrivate" class="mt-4 rounded-2xl border border-white/10 p-6 bg-white/5">
        <div class="text-lg">🔒 {{ privateMessage || 'Bu hesap gizlidir.' }}</div>
      </div>

      <div v-else class="grid gap-6">
        <!-- Posts -->
        <div class="rounded-2xl border border-white/10 p-6">
          <h2 class="text-xl font-semibold mb-4">Posts</h2>
          <div v-if="posts.length === 0" class="text-white/60">No posts.</div>
          <div v-else class="grid gap-4">
            <div v-for="p in posts" :key="p.id" class="rounded-xl border border-white/10 p-4">
              <div class="font-semibold">{{ p.title }}</div>
              <div class="text-white/70 mt-1">{{ p.body }}</div>
              <div class="flex items-center gap-3 text-sm text-white/70 mt-3">
                <button @click="likePost(p)" class="px-3 py-1 rounded-lg border border-white/10 hover:border-white/20">❤️ {{ p.likes_count || 0 }}</button>
                <button @click="openPostComments(p)" class="px-3 py-1 rounded-lg border border-white/10 hover:border-white/20">💬 {{ p.comments_count || 0 }}</button>
              </div>
              <div v-if="openPostId === p.id" class="mt-3 grid gap-2">
                <div v-if="postComments.length === 0" class="text-white/60">No comments.</div>
                <div v-else class="grid gap-2">
                  <div v-for="c in postComments" :key="c.id" class="rounded border border-white/10 p-2">
                    <div class="text-sm text-white/60">{{ c.user?.username || 'User' }}</div>
                    <div>{{ c.body }}</div>
                  </div>
                </div>
                <div class="flex gap-2">
                  <input v-model="newPostComment" placeholder="Add a comment" class="flex-1 rounded border border-white/10 bg-transparent px-3 py-2" />
                  <button @click="addPostComment" :disabled="commenting || !newPostComment.trim()" class="px-3 py-2 rounded bg-indigo-600 text-white disabled:opacity-60">Send</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Albums -->
        <div class="rounded-2xl border border-white/10 p-6">
          <h2 class="text-xl font-semibold mb-4">Albums</h2>
          <div v-if="albums.length === 0" class="text-white/60">No albums.</div>
          <div v-else class="grid gap-4">
            <div v-for="a in albums" :key="a.id" class="rounded-xl border border-white/10 p-4">
              <div class="font-semibold">{{ a.title }}</div>
              <div class="flex items-center gap-3 text-sm text-white/70 mt-3">
                <button @click="likeAlbum(a)" class="px-3 py-1 rounded-lg border border-white/10 hover:border-white/20">❤️ {{ a.likes_count || 0 }}</button>
                <button @click="openAlbumComments(a)" class="px-3 py-1 rounded-lg border border-white/10 hover:border-white/20">💬 {{ a.comments_count || 0 }}</button>
              </div>
              <div v-if="openAlbumId === a.id" class="mt-3 grid gap-2">
                <div v-if="albumComments.length === 0" class="text-white/60">No comments.</div>
                <div v-else class="grid gap-2">
                  <div v-for="c in albumComments" :key="c.id" class="rounded border border-white/10 p-2">
                    <div class="text-sm text-white/60">{{ c.user?.username || 'User' }}</div>
                    <div>{{ c.body }}</div>
                  </div>
                </div>
                <div class="flex gap-2">
                  <input v-model="newAlbumComment" placeholder="Add a comment" class="flex-1 rounded border border-white/10 bg-transparent px-3 py-2" />
                  <button @click="addAlbumComment" :disabled="commenting || !newAlbumComment.trim()" class="px-3 py-2 rounded bg-indigo-600 text-white disabled:opacity-60">Send</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
