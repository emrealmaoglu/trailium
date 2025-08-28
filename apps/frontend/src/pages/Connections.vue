<script setup>
import { ref, onMounted } from 'vue'
import { json } from '@/lib/http'

const activeTab = ref('followers') // followers | following | requests
const followers = ref([])
const following = ref([])
const requests = ref([])
const loading = ref(false)
const errorMsg = ref('')

async function fetchFollowers() {
  followers.value = await json('/api/follows/followers')
}

async function fetchFollowing() {
  following.value = await json('/api/follows/following')
}

async function fetchRequests() {
  requests.value = await json('/api/follows/pending')
}

async function loadTab(tab) {
  activeTab.value = tab
  loading.value = true
  errorMsg.value = ''
  try {
    if (tab === 'followers') await fetchFollowers()
    else if (tab === 'following') await fetchFollowing()
    else await fetchRequests()
  } catch (e) {
    errorMsg.value = 'Could not load data.'
  } finally {
    loading.value = false
  }
}

async function approve(id) {
  await json(`/api/follows/${id}/approve/`, { method: 'POST' })
  await fetchRequests()
  await fetchFollowers()
}

async function reject(id) {
  await json(`/api/follows/${id}/reject/`, { method: 'POST' })
  await fetchRequests()
}

onMounted(() => loadTab('followers'))
</script>

<template>
  <section class="connections">
    <div class="header">
      <h1>Connections</h1>
    </div>

    <div class="tabs">
      <button @click="loadTab('followers')" :class="['tab', { active: activeTab==='followers' }]">
        <span>Followers</span>
        <span class="badge" :class="{ active: activeTab==='followers' }">{{ followers.length }}</span>
      </button>
      <button @click="loadTab('following')" :class="['tab', { active: activeTab==='following' }]">
        <span>Following</span>
        <span class="badge" :class="{ active: activeTab==='following' }">{{ following.length }}</span>
      </button>
      <button @click="loadTab('requests')" :class="['tab', { active: activeTab==='requests' }]">
        <span>Requests</span>
        <span class="badge" :class="{ active: activeTab==='requests' }">{{ requests.length }}</span>
      </button>
    </div>

    <div v-if="loading" class="panel">Loading…</div>
    <div v-else-if="errorMsg" class="panel muted">{{ errorMsg }}</div>

    <div v-else class="list">
      <template v-if="activeTab==='followers'">
        <div v-if="followers.length===0" class="panel muted center">No followers yet.</div>
        <div v-else class="items">
          <div v-for="f in followers" :key="f.id" class="item">
            <div class="left">
              <div class="avatar">
                {{ (f.follower?.username||'U').charAt(0).toUpperCase() }}
              </div>
              <div class="name">{{ f.follower?.username }}</div>
            </div>
          </div>
        </div>
      </template>

      <template v-else-if="activeTab==='following'">
        <div v-if="following.length===0" class="panel muted center">You are not following anyone.</div>
        <div v-else class="items">
          <div v-for="f in following" :key="f.id" class="item">
            <div class="left">
              <div class="avatar">
                {{ (f.followed?.username||'U').charAt(0).toUpperCase() }}
              </div>
              <div class="name">{{ f.followed?.username }}</div>
            </div>
          </div>
        </div>
      </template>

      <template v-else>
        <div v-if="requests.length===0" class="panel muted center">No pending requests.</div>
        <div v-else class="items">
          <div v-for="r in requests" :key="r.id" class="item">
            <div class="left">
              <div class="avatar">
                {{ (r.follower?.username||'U').charAt(0).toUpperCase() }}
              </div>
              <div class="name">{{ r.follower?.username }}</div>
            </div>
            <div class="actions">
              <button @click="approve(r.id)" class="btn success">Accept</button>
              <button @click="reject(r.id)" class="btn danger">Reject</button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </section>
</template>

<style scoped>
.connections {
  max-width: 880px;
  margin: 0 auto;
  padding: 24px;
}

.header h1 {
  font-size: 24px;
  font-weight: 700;
  color: var(--c-text);
  margin: 0;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 10px;
  background: var(--c-surface-2);
  color: var(--c-text);
  border: 1px solid var(--c-border);
  cursor: pointer;
}

.tab.active {
  background: var(--c-accent);
  border-color: var(--c-accent);
  color: #fff;
}

.badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--c-surface);
  color: var(--c-text);
  border: 1px solid var(--c-border);
}

.badge.active {
  background: rgba(255,255,255,0.25);
  color: #fff;
  border-color: transparent;
}

.panel {
  margin-top: 16px;
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-text);
  border-radius: 16px;
  padding: 16px;
}

.panel.muted {
  color: var(--c-text-muted);
}

.panel.center {
  text-align: center;
}

.list {
  margin-top: 16px;
}

.items {
  display: grid;
  gap: 8px;
}

.item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-text);
  border-radius: 12px;
  padding: 12px;
  transition: border-color .2s ease;
}

.item:hover { border-color: var(--c-accent); }

.left { display: flex; align-items: center; gap: 12px; }

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 600;
  background: linear-gradient(135deg, #ec4899 0%, #60a5fa 100%);
}

.name { font-weight: 600; }

.actions { display: flex; gap: 8px; }

.btn {
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid var(--c-border);
  background: var(--c-surface-2);
  color: var(--c-text);
  cursor: pointer;
}

.btn.success {
  background: #16a34a;
  color: #fff;
  border-color: #16a34a;
}

.btn.danger {
  background: #dc2626;
  color: #fff;
  border-color: #dc2626;
}
</style>


