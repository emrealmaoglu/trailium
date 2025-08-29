<template>
  <div class="posts-page">
    <div class="add-line">
      <input v-model="title" :placeholder="$t('posts.addPost') as string" class="inp" @keydown.enter="onCreate" />
      <button class="btn" @click="onCreate">+</button>
    </div>
    <div v-if="store.loading" class="skl"></div>
    <div v-else-if="store.posts.length === 0" class="empty">{{ $t('posts.empty') }}</div>
    <div class="grid">
      <PostCard v-for="p in store.posts" :key="p.id" :post="p" @open="open(p)" @like="store.like(p.id)" />
    </div>
    <Pagination :page="store.page" :total-pages="store.totalPages" :disabled="store.loading" @update:page="onChangePage" />
    <PostModal v-if="active" :post="active" @close="active=null" @like="store.like(active!.id)" @add-comment="onAddComment" />
  </div>
</template>

<script setup lang="ts">
/** Kullanıcı gönderileri sekmesi. */
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePostsStore } from '@/stores/posts'
import PostCard from '@/components/PostCard.vue'
import PostModal from '@/components/PostModal.vue'
import Pagination from '@/components/Pagination.vue'

const route = useRoute(); const router = useRouter()
const store = usePostsStore()
const title = ref('')
const active = ref<any|null>(null)
const userId = Number(route.params.id)

onMounted(async () => {
  const p = Number(route.query.page ?? 1) || 1
  await store.fetchPosts(userId, { page: p, pageSize: store.pageSize })
})

async function onCreate() {
  const t = title.value.trim(); if (!t) return
  await store.createPost({ title: t })
  title.value = ''
}

function onChangePage(p: number) {
  store.fetchPosts(userId, { page: p, pageSize: store.pageSize })
  router.push({ query: { ...route.query, page: String(p) } })
}

function open(p: any) { active.value = p }
async function onAddComment(body: string) { if (active.value) await store.addComment(active.value.id, body) }
</script>

<style scoped>
.posts-page { display: grid; gap: 12px; }
.add-line { display: flex; gap: 8px; }
.inp { flex: 1; border: 1px solid var(--c-border); border-radius: 8px; padding: 8px 10px; }
.btn { border: 1px solid var(--c-border); background: var(--c-surface-2); border-radius: 8px; padding: 8px 10px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
.empty { color: var(--c-text-muted); font-size: 14px; text-align: center; padding: 16px; }
.skl { height: 80px; border-radius: 10px; background: var(--c-surface-2); animation: pulse 1.2s ease-in-out infinite; }
@keyframes pulse { 0%{opacity:.6} 50%{opacity:.95} 100%{opacity:.6} }
</style>


