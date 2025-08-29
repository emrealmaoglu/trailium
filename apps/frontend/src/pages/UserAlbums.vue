<template>
  <div class="albums-page">
    <div class="add-line">
      <input v-model="title" :placeholder="$t('albums.addAlbum') as string" class="inp" @keydown.enter="onCreate" />
      <button class="btn" @click="onCreate">+</button>
    </div>
    <div v-if="store.loading" class="skl"></div>
    <div v-else-if="store.albums.length === 0" class="empty">{{ $t('albums.empty') }}</div>
    <div class="grid">
      <AlbumCard v-for="a in store.albums" :key="a.id" :album="a" @open="open(a)" />
    </div>
    <Pagination :page="store.page" :total-pages="store.totalPages" :disabled="store.loading" @update:page="onChangePage" />
    <AlbumModal v-if="active" :album="active" @close="active=null" @add-photo="onAddPhoto" />
  </div>
</template>

<script setup lang="ts">
/** Kullanıcı albümleri sekmesi. */
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAlbumsStore } from '@/stores/albums'
import AlbumCard from '@/components/AlbumCard.vue'
import AlbumModal from '@/components/AlbumModal.vue'
import Pagination from '@/components/Pagination.vue'

const route = useRoute(); const router = useRouter()
const store = useAlbumsStore()
const title = ref('')
const active = ref<any|null>(null)
const userId = Number(route.params.id)

onMounted(async () => {
  const p = Number(route.query.page ?? 1) || 1
  await store.fetchAlbums(userId, { page: p, pageSize: store.pageSize })
})

async function onCreate() {
  const t = title.value.trim(); if (!t) return
  await store.createAlbum({ title: t })
  title.value = ''
}

function onChangePage(p: number) {
  store.fetchAlbums(userId, { page: p, pageSize: store.pageSize })
  router.push({ query: { ...route.query, page: String(p) } })
}

function open(a: any) { active.value = a }
async function onAddPhoto(url: string) { if (active.value) await store.addPhoto(active.value.id, { url }) }
</script>

<style scoped>
.albums-page { display: grid; gap: 12px; }
.add-line { display: flex; gap: 8px; }
.inp { flex: 1; border: 1px solid var(--c-border); border-radius: 8px; padding: 8px 10px; }
.btn { border: 1px solid var(--c-border); background: var(--c-surface-2); border-radius: 8px; padding: 8px 10px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
.empty { color: var(--c-text-muted); font-size: 14px; text-align: center; padding: 16px; }
.skl { height: 80px; border-radius: 10px; background: var(--c-surface-2); animation: pulse 1.2s ease-in-out infinite; }
@keyframes pulse { 0%{opacity:.6} 50%{opacity:.95} 100%{opacity:.6} }
</style>


