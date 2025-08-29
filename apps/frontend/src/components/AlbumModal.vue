<template>
  <div class="overlay" @click.self="$emit('close')">
    <div class="modal">
      <header class="hdr">
        <h3 class="title">{{ album.title }}</h3>
        <button class="close" @click="$emit('close')">×</button>
      </header>
      <div class="grid">
        <PhotoThumb v-for="p in photos" :key="p.id" :src="p.thumbnail_url || p.url || p.file_url" :title="p.title" />
      </div>
      <div class="add" v-if="canEdit">
        <input v-model="photoUrl" :placeholder="$t('photos.addPhoto') as string" class="inp" @keydown.enter="add" />
        <button class="btn" @click="add">+</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/** Albüm detay modalı (fotoğraflar). */
import { ref, onMounted } from 'vue'
import PhotoThumb from './PhotoThumb.vue'

const props = defineProps<{ album: any; canEdit?: boolean }>()
const emit = defineEmits<{ 'close':[], 'add-photo':[string] }>()
const photos = ref<any[]>(props.album.photos || [])
const photoUrl = ref('')

function add() {
  const url = photoUrl.value.trim(); if (!url) return
  emit('add-photo', url)
  photoUrl.value = ''
}

onMounted(() => { /* photos could be refreshed by parent via store */ })
</script>

<style scoped>
.overlay { position: fixed; inset: 0; background: rgba(0,0,0,.35); display: grid; place-items: center; }
.modal { width: min(860px, 96vw); background: var(--c-surface); color: var(--c-text); border-radius: 12px; border: 1px solid var(--c-border); padding: 12px; }
.hdr { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.title { margin: 0; font-size: 18px; font-weight: 700; }
.close { border: none; background: transparent; font-size: 20px; cursor: pointer; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 8px; }
.add { display: flex; gap: 8px; margin-top: 10px; }
.inp { flex: 1; border: 1px solid var(--c-border); border-radius: 8px; padding: 8px 10px; }
.btn { border: 1px solid var(--c-border); background: var(--c-surface-2); border-radius: 8px; padding: 6px 10px; }
</style>


