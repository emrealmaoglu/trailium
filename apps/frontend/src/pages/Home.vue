<script setup>
import { ref, onMounted } from 'vue'
import { json } from '@/lib/http'

const loading = ref(true)
const items = ref([])
const errorMsg = ref('')

async function load() {
  loading.value = true
  errorMsg.value = ''
  try {
    const data = await json('/api/feed/posts?page_size=6')
    items.value = data.results || []
  } catch {
    errorMsg.value = 'Unable to load followed users\' latest posts.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section>
    <div style="margin-bottom: 32px;">
      <h1 style="font-size: 32px; font-weight: 700; margin-bottom: 12px; color: var(--c-text);">
        Welcome to Trailium 👋
      </h1>
      <p style="font-size: 18px; color: var(--c-text-muted); line-height: 1.6;">
        Your comprehensive social platform for managing users, todos, posts, and albums.
      </p>
    </div>

    <div class="grid grid-cols-responsive" style="gap: 24px;">
      <div class="card" style="padding: 24px; cursor: pointer;" @click="$router.push('/users')">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #ff4db0, #4db2ff); border-radius: 12px; display: grid; place-items: center; color: white; font-size: 24px;">
            👥
          </div>
          <div>
            <h3 style="font-size: 20px; font-weight: 600; margin: 0; color: var(--c-text);">Users</h3>
            <p style="margin: 4px 0 0; color: var(--c-text-muted);">Browse and connect with users</p>
          </div>
        </div>
        <p style="color: var(--c-text-muted); line-height: 1.5;">
          Discover users, view profiles, and manage your connections. Follow users to see their content.
        </p>
      </div>

      <div class="card" style="padding: 24px; cursor: pointer;" @click="$router.push('/todos')">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #4db2ff, #4dffb2); border-radius: 12px; display: grid; place-items: center; color: white; font-size: 24px;">
            ✅
          </div>
          <div>
            <h3 style="font-size: 20px; font-weight: 600; margin: 0; color: var(--c-text);">Todos</h3>
            <p style="margin: 4px 0 0; color: var(--c-text-muted);">Manage your tasks and lists</p>
          </div>
        </div>
        <p style="color: var(--c-text-muted); line-height: 1.5;">
          Create and organize your todo lists with progress tracking. Break down tasks into subtasks.
        </p>
      </div>

      <div class="card" style="padding: 24px; cursor: pointer;" @click="$router.push('/posts')">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #4dffb2, #b24dff); border-radius: 12px; display: grid; place-items: center; color: white; font-size: 24px;">
            📝
          </div>
          <div>
            <h3 style="font-size: 20px; font-weight: 600; margin: 0; color: var(--c-text);">Posts</h3>
            <p style="margin: 4px 0 0; color: var(--c-text-muted);">Share and discover content</p>
          </div>
        </div>
        <p style="color: var(--c-text-muted); line-height: 1.5;">
          Read posts from users, like and comment on content.
        </p>
      </div>

      <div class="card" style="padding: 24px; cursor: pointer;" @click="$router.push('/albums')">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #b24dff, #ff4db0); border-radius: 12px; display: grid; place-items: center; color: white; font-size: 24px;">
            📸
          </div>
          <div>
            <h3 style="font-size: 20px; font-weight: 600; margin: 0; color: var(--c-text);">Albums</h3>
            <p style="margin: 4px 0 0; color: var(--c-text-muted);">Organize your photos</p>
          </div>
        </div>
        <p style="color: var(--c-text-muted); line-height: 1.5;">
          Create photo albums and organize your memories.
        </p>
      </div>

      <div class="card" style="padding: 24px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
          <div style="font-weight:700;">Latest from people you follow</div>
        </div>
        <div v-if="errorMsg" style="color:var(--c-text-muted);">{{ errorMsg }}</div>
        <div v-else-if="loading" style="color:var(--c-text-muted);">Loading…</div>
        <div v-else-if="items.length === 0" style="color:var(--c-text-muted);">No recent posts from followed users.</div>
        <ul v-else style="list-style:none; padding:0; margin:0; display:grid; gap:12px;">
          <li v-for="p in items" :key="p.id" class="card" style="padding:12px;">
            <div style="display:flex; align-items:center; gap:8px;">
              <div style="width:28px; height:28px; border-radius:50%; background:linear-gradient(135deg,#ff4db0,#4db2ff); display:grid; place-items:center; color:#fff; font-weight:600; font-size:12px;">
                {{ (p.user?.username || 'U').charAt(0).toUpperCase() }}
              </div>
              <div style="font-weight:600;">{{ p.user?.username || 'User' }}</div>
              <div style="margin-left:auto; color:var(--c-text-muted); font-size:12px;">{{ new Date(p.created_at).toLocaleString() }}</div>
            </div>
            <div style="margin-top:8px; color:var(--c-text);">{{ p.title }}</div>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>
