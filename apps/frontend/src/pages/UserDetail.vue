<template>
  <div class="detail-page">
    <div v-if="loading" class="skeleton">
      <div class="avatar sk"></div>
      <div class="lines">
        <div class="sk line"></div>
        <div class="sk line small"></div>
      </div>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <router-link to="/users" class="back">← {{ t('users.title') }}</router-link>
    </div>

    <div v-else-if="!user" class="empty">
      <p>{{ t('user.notFound') }}</p>
      <router-link to="/users" class="back">← {{ t('users.title') }}</router-link>
    </div>

    <div v-else class="header">
      <div class="avatar" v-if="user.avatar"><img :src="user.avatar" :alt="user.username" /></div>
      <div class="avatar placeholder" v-else>{{ (user.full_name || user.username).slice(0,1).toUpperCase() }}</div>
      <div class="meta">
        <h2 class="name">{{ user.full_name || user.username }}</h2>
        <div class="username">@{{ user.username }}</div>
      </div>
    </div>

    <div class="tabs">
      <button class="tab active">{{ t('user.tabs.todos') }}</button>
      <button class="tab" disabled>{{ t('user.tabs.posts') }} – {{ t('user.comingSoon') }}</button>
      <button class="tab" disabled>{{ t('user.tabs.albums') }} – {{ t('user.comingSoon') }}</button>
    </div>
    <UserTodos />
  </div>
</template>

<script setup lang="ts">
/** Kullanıcı detay iskelet sayfası (başlık + sekme yer tutucular). */
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { json } from '@/lib/http'
import { useI18n } from 'vue-i18n'
import UserTodos from './UserTodos.vue'

const route = useRoute()
const { t } = useI18n()

const loading = ref(true)
const error = ref<string|null>(null)
const user = ref<any>(null)

onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    const id = route.params.id
    user.value = await json(`/api/users/${id}/`)
  } catch (err: any) {
    error.value = err?.message || 'Failed to load user'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-page { max-width: 840px; margin: 0 auto; padding: 16px; }
.header { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }
.avatar { width: 72px; height: 72px; border-radius: 50%; overflow: hidden; background: var(--c-surface-2); display: grid; place-items: center; font-weight: 700; }
.avatar img { width: 100%; height: 100%; object-fit: cover; }
.meta .name { font-size: 20px; font-weight: 700; color: var(--c-text); }
.meta .username { font-size: 13px; color: var(--c-text-muted); }
.tabs { display: flex; gap: 8px; margin-top: 12px; }
.tab { padding: 8px 12px; border-radius: 8px; border: 1px solid var(--c-border); background: var(--c-surface); color: var(--c-text-muted); }
.skeleton { display: flex; align-items: center; gap: 16px; }
.sk { background: var(--c-surface-2); border-radius: 8px; animation: pulse 1.2s ease-in-out infinite; }
.skeleton .avatar.sk { width: 72px; height: 72px; border-radius: 50%; }
.skeleton .line { width: 220px; height: 14px; }
.skeleton .line.small { width: 140px; height: 12px; }
.error, .empty { text-align: center; color: var(--c-text-muted); }
.back { color: var(--c-accent); }
@keyframes pulse { 0% { opacity: .6 } 50% { opacity: .95 } 100% { opacity: .6 } }
</style>


