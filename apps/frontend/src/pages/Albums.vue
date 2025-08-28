<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { json } from '@/lib/http'

const loading = ref(true)
const errorMsg = ref('')
const albums = ref([])
const photos = ref([])
const activeAlbumId = ref(null)
const creating = ref(false)
const newTitle = ref('')
const uploading = ref(false)
const photoTitle = ref('')
const photoUrl = ref('')
const photoFile = ref(null)
const showUploadForm = ref(false)
const createModalOpen = ref(false)

async function fetchAlbums() {
  loading.value = true
  errorMsg.value = ''
  try {
    const payload = await json('/api/albums/')
    albums.value = payload.results || payload
    if (albums.value.length) selectAlbum(albums.value[0].id)
    else photos.value = []
  } catch {
    errorMsg.value = 'Could not load albums.'
  } finally {
    loading.value = false
  }
}

async function selectAlbum(id) {
  activeAlbumId.value = id
  try {
    photos.value = await json(`/api/albums/${id}/photos/`)
  } catch {
    photos.value = []
  }
}

async function createAlbum() {
  if (!newTitle.value.trim()) return
  creating.value = true
  try {
    const form = new FormData()
    form.append('title', newTitle.value)
    form.append('is_published', 'true')
    form.append('visibility', 'public')
    await json('/api/albums/', { method: 'POST', body: form })
    newTitle.value = ''
    await fetchAlbums()
    createModalOpen.value = false
  } finally {
    creating.value = false
  }
}

async function uploadPhoto() {
  if (!activeAlbumId.value) return
  if (!photoTitle.value.trim() && !photoFile.value) return

  uploading.value = true
  try {
    const form = new FormData()
    if (photoTitle.value) form.append('title', photoTitle.value)
    if (photoFile.value) form.append('file', photoFile.value)
    else if (photoUrl.value) {
      // Fallback: allow url-based upload too
      form.append('url', photoUrl.value)
    }
    await json(`/api/albums/${activeAlbumId.value}/photos/`, { method: 'POST', body: form })

    photoTitle.value = ''
    photoUrl.value = ''
    photoFile.value = null
    showUploadForm.value = false
    await selectAlbum(activeAlbumId.value)
  } catch (e) {
    errorMsg.value = 'Could not upload photo.'
  } finally {
    uploading.value = false
  }
}

function handleUrlPrefill() {
  if (photoUrl.value && !photoTitle.value) {
    try {
      const u = new URL(photoUrl.value)
      const last = u.pathname.split('/').filter(Boolean).pop() || ''
      photoTitle.value = last || 'Photo'
    } catch {}
  }
}

onMounted(() => {
  fetchAlbums()
  const onVis = () => { if (document.visibilityState === 'visible') fetchAlbums() }
  document.addEventListener('visibilitychange', onVis)
  onUnmounted(() => document.removeEventListener('visibilitychange', onVis))
})
</script>

<template>
  <div class="container">
    <div style="display:flex; align-items:center; gap:8px; margin:0 0 16px;">
      <h2 style="margin:0; font-size:22px; font-weight:700;">Photo Albums</h2>
      <button @click="createModalOpen = true" style="margin-left:auto; border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:10px; padding:10px 16px; cursor:pointer; font-size:14px; font-weight:500; display:flex; align-items:center; gap:8px;">
        <span>✏️</span>
        Create Album
      </button>
    </div>

    <!-- Create Album Modal -->
    <div v-if="createModalOpen" class="modal-overlay" @click="createModalOpen = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header" style="display:flex; align-items:center; justify-content:space-between; padding:16px; border-bottom:1px solid var(--c-border);">
          <h3 style="margin:0; font-size:18px; font-weight:700;">Create New Album</h3>
          <button @click="createModalOpen = false" class="close-btn" style="background:none; border:none; font-size:22px; cursor:pointer; color:var(--c-text-muted);">×</button>
        </div>

        <div class="modal-body" style="padding:16px;">
          <form @submit.prevent="createAlbum" style="display:grid; gap:12px;">
            <div>
              <label style="display:block; font-weight:500; margin-bottom:6px; font-size:13px;">Album Title</label>
              <input v-model="newTitle" placeholder="Enter album title" required style="width:100%; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px;" />
            </div>
          </form>
        </div>

        <div class="modal-footer" style="display:flex; gap:8px; justify-content:flex-end; padding:16px; border-top:1px solid var(--c-border);">
          <button @click="createModalOpen = false" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:8px; padding:8px 16px; cursor:pointer; font-size:13px;">Cancel</button>
          <button @click="createAlbum" :disabled="creating || !newTitle.trim()" style="border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:8px; padding:8px 16px; cursor:pointer; font-size:13px; font-weight:500;">
            {{ creating ? 'Creating…' : 'Create Album' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="card" style="padding:16px;">Loading…</div>
    <div v-else-if="errorMsg" class="card" style="padding:16px; color:var(--c-text-muted);">{{ errorMsg }}</div>

    <div v-else-if="albums.length === 0" class="card" style="padding:32px; text-align:center; color:var(--c-text-muted);">
      <div style="font-size:48px; margin-bottom:16px;">📸</div>
      <div style="font-size:18px; font-weight:600; margin-bottom:8px;">No albums yet</div>
      <div>Create your first album to get started!</div>
    </div>

    <div v-else style="display:grid; grid-template-columns: 280px 1fr; gap:20px; align-items:start;">
      <!-- Album List -->
      <div class="card" style="padding:16px;">
        <h3 style="margin:0 0 16px; font-size:16px; font-weight:600;">Your Albums</h3>
        <ul style="list-style:none; padding:0; margin:0; display:grid; gap:8px;">
          <li v-for="a in albums" :key="a.id">
            <button @click="selectAlbum(a.id)" :aria-pressed="a.id===activeAlbumId" style="width:100%; text-align:left; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:12px; cursor:pointer; font-weight:600; transition: all 0.2s ease; hover:background:var(--c-surface-2);" :style="a.id===activeAlbumId ? 'background:var(--c-accent); color:white; border-color:var(--c-accent);' : ''">
              {{ a.title }}
            </button>
          </li>
        </ul>
      </div>

      <!-- Photo Grid -->
      <div class="card" style="padding:20px; min-height:400px;">
        <div v-if="!activeAlbumId" style="color:var(--c-text-muted); text-align:center; padding:40px;">
          <div style="font-size:24px; margin-bottom:8px;">📁</div>
          <div>Select an album to view photos</div>
        </div>

        <div v-else>
          <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:20px;">
            <h3 style="margin:0; font-size:18px; font-weight:600;">
              {{ albums.find(a => a.id === activeAlbumId)?.title }}
            </h3>
            <button @click="showUploadForm = !showUploadForm" style="border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:10px; padding:8px 16px; cursor:pointer; font-size:13px; font-weight:500;">
              {{ showUploadForm ? 'Cancel' : 'Add Photo' }}
            </button>
          </div>

          <!-- Upload Form -->
          <div v-if="showUploadForm" class="card" style="padding:16px; margin-bottom:20px; border:2px dashed var(--c-border); background:var(--c-surface-2);">
            <h4 style="margin:0 0 12px; font-size:14px; font-weight:600;">Upload New Photo</h4>
            <form @submit.prevent="uploadPhoto" style="display:grid; gap:12px;">
              <div>
                <label style="display:block; font-weight:500; margin-bottom:6px; font-size:13px;">Photo Title</label>
                <input v-model="photoTitle" placeholder="Enter photo title" required style="width:100%; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:8px; padding:8px 10px; font-size:13px;" />
              </div>

              <div>
                <label style="display:block; font-weight:500; margin-bottom:6px; font-size:13px;">Choose Image</label>
                <input type="file" accept="image/*" @change="e => { photoFile.value = e.target.files?.[0] || null }" />
                <div style="font-size:12px; color:var(--c-text-muted); margin-top:6px;">or paste an image URL:</div>
                <input v-model="photoUrl" @blur="handleUrlPrefill" type="url" placeholder="https://example.com/image.jpg" style="width:100%; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:8px; padding:8px 10px; font-size:13px;" />
              </div>

              <div style="display:flex; gap:8px; justify-content:flex-end;">
                <button type="button" @click="showUploadForm = false" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:8px; padding:8px 16px; cursor:pointer; font-size:13px;">Cancel</button>
                <button type="submit" :disabled="uploading || !photoTitle.trim() || (!photoFile && !photoUrl.trim())" style="border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:8px; padding:8px 16px; cursor:pointer; font-size:13px; font-weight:500;">
                  {{ uploading ? 'Uploading…' : 'Upload Photo' }}
                </button>
              </div>
            </form>
          </div>

          <!-- Photos Grid -->
          <div v-if="photos.length === 0" style="color:var(--c-text-muted); text-align:center; padding:40px;">
            <div style="font-size:32px; margin-bottom:8px;">🖼️</div>
            <div>No photos in this album yet</div>
            <div style="font-size:13px; margin-top:4px;">Add your first photo!</div>
          </div>

          <div v-else class="grid" style="grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap:16px;">
            <div v-for="p in photos" :key="p.id" class="card" style="padding:12px; text-align:center; transition: all 0.2s ease; hover:transform:scale(1.02);">
              <img :src="p.thumbnail_url_file || p.thumbnail_url || p.file_url || p.url" :alt="p.title || 'Photo'" style="width:100%; height:140px; object-fit:cover; border-radius:8px; margin-bottom:8px;" />
              <div style="font-size:13px; font-weight:500; color:var(--c-text);">{{ p.title || 'Untitled' }}</div>
              <div v-if="p.created_at" style="font-size:11px; color:var(--c-text-muted); margin-top:4px;">
                {{ new Date(p.created_at).toLocaleDateString() }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
