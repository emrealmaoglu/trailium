<script setup>
import { ref, onMounted, onUnmounted, inject } from 'vue'
import { json } from '@/lib/http'
import { PAGE_SIZE_ALBUMS } from '@/config/constants'
import ErrorCard from '@/components/ui/ErrorCard.vue'

const showNotification = inject('showNotification')

const loading = ref(true)
const errorMsg = ref('')
const albums = ref([])
const photos = ref([])
const activeAlbumId = ref(null)
const creating = ref(false)
const newTitle = ref('')
const uploading = ref(false)
const photoFile = ref(null)
const photoTitle = ref('')
const photoCaption = ref('')
const showUploadForm = ref(false)

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
    await json('/api/albums/', { method: 'POST', body: JSON.stringify({ title: newTitle.value }) })
    newTitle.value = ''
    await fetchAlbums()
  } finally {
    creating.value = false
  }
}

async function uploadPhoto() {
  if (!photoFile.value || !activeAlbumId.value) return

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('title', photoTitle.value.trim() || '')
    formData.append('caption', photoCaption.value.trim() || '')
    formData.append('image', photoFile.value)

    const response = await json(`/api/albums/${activeAlbumId.value}/photos/`, {
      method: 'POST',
      body: formData,
      headers: {} // Let browser set content-type for FormData
    })

    // Add the new photo to the current album's photos
    if (selectedAlbum.value) {
      selectedAlbum.value.photos.unshift(response)
    }

    photoTitle.value = ''
    photoCaption.value = ''
    photoFile.value = null
    showUploadForm.value = false
    showNotification('Photo uploaded successfully!', 'success', 3000)
  } catch (e) {
    console.error('Upload error:', e)
    if (e.status === 413) {
      showNotification('File too large. Maximum size is 5MB.', 'error', 5000)
    } else if (e.status === 400) {
      showNotification('Invalid file type. Please upload an image.', 'error', 5000)
    } else {
      showNotification('Failed to upload photo. Please try again.', 'error', 5000)
    }
  } finally {
    uploading.value = false
  }
}

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) {
    if (!file.type.startsWith('image/')) {
      showNotification('Please select an image file.', 'error', 3000)
      return
    }
    if (file.size > 5 * 1024 * 1024) { // 5MB limit
      showNotification('File too large. Maximum size is 5MB.', 'error', 3000)
      return
    }
    photoFile.value = file
    if (!photoTitle.value) {
      photoTitle.value = file.name.replace(/\.[^/.]+$/, '') // Remove extension
    }
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
      <h2 style="margin:0; font-size:22px; font-weight:700;">Photo Albums <span style="font-size:14px; color:var(--c-text-muted);">(Page size: {{ PAGE_SIZE_ALBUMS }})</span></h2>
      <button @click="fetchAlbums" style="margin-left:auto; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:8px 12px; cursor:pointer; font-size:13px;">Refresh</button>
    </div>

    <!-- Create Album Form -->
    <div class="card" style="padding:16px; margin-bottom:16px;">
      <h3 style="margin:0 0 12px; font-size:16px; font-weight:600;">Create New Album</h3>
      <form @submit.prevent="createAlbum" style="display:flex; gap:12px; align-items:center;">
        <input v-model="newTitle" placeholder="Enter album title" required style="flex:1; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px;" />
        <button :disabled="creating || !newTitle.trim()" style="border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:10px; padding:10px 16px; cursor:pointer; font-size:14px; font-weight:500;">
          {{ creating ? 'Creating…' : 'Create Album' }}
        </button>
      </form>
    </div>

    <div v-if="loading" class="grid" style="grid-template-columns: 280px 1fr; gap:20px;">
      <div class="card" style="padding:16px; height:240px;"></div>
      <div class="card" style="padding:20px; min-height:400px;"></div>
    </div>
    <ErrorCard
      v-else-if="errorMsg"
      title="Couldn't load albums"
      :message="errorMsg"
      :showRetry="true"
      @retry="fetchAlbums"
    />

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
                <input v-model="photoTitle" placeholder="Enter photo title" style="width:100%; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:8px; padding:8px 10px; font-size:13px;" />
              </div>

              <div>
                <label style="display:block; font-weight:500; margin-bottom:6px; font-size:13px;">Caption (optional)</label>
                <textarea v-model="photoCaption" placeholder="Enter photo caption" rows="2" style="width:100%; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:8px; padding:8px 10px; font-size:13px; resize:vertical;"></textarea>
              </div>

              <div>
                <label style="display:block; font-weight:500; margin-bottom:6px; font-size:13px;">Select Image (max 5MB)</label>
                <input type="file" @change="handleFileSelect" accept="image/*" required style="width:100%; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:8px; padding:8px 10px; font-size:13px;" />
              </div>

              <div style="display:flex; gap:8px; justify-content:flex-end;">
                <button type="button" @click="showUploadForm = false" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:8px; padding:8px 16px; cursor:pointer; font-size:13px;">Cancel</button>
                <button type="submit" :disabled="uploading || !photoFile || !photoTitle.trim()" style="border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:8px; padding:8px 16px; cursor:pointer; font-size:13px; font-weight:500;">
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
              <img :src="p.thumbnail_url || p.url" :alt="p.title || 'Photo'" style="width:100%; height:140px; object-fit:cover; border-radius:8px; margin-bottom:8px;" />
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
