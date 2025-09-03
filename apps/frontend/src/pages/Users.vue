<script setup>
import { ref, onMounted, onUnmounted, computed, inject } from 'vue'
import { json } from '@/lib/http'
import UserCard from '@/components/UserCard.vue'
import UserCardSkeleton from '@/components/UserCardSkeleton.vue'
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import { useSessionStore } from '@/stores/session'

const loading = ref(true)
const users = ref([])
const errorMsg = ref('')
const page = ref(1)
const nextUrl = ref('')
const prevUrl = ref('')
const total = ref(0)

const searchQuery = ref('')
const searchTimeout = ref(null)
const showFilters = ref(false)
const filterPremium = ref(false)
const filterPrivate = ref(false)

const session = useSessionStore()
const showNotification = inject('showNotification')

function mapUser(u) {
  return {
    id: u.id,
    name: u.full_name || u.username,
    email: u.email,
    phone: u.phone,
    addressText: u.address || '',
    companyName: '',
    website: '',
    is_premium: u.is_premium || false,
    is_private: u.is_private || false,
  }
}

function getPageFromUrl(url) {
  try {
    const u = new URL(url)
    const p = u.searchParams.get('page')
    return p ? parseInt(p, 10) : null
  } catch { return null }
}

async function fetchData(input = `/api/users/?page=${page.value}`) {
  loading.value = true
  errorMsg.value = ''
  try {
    const payload = await json(input)
    const data = Array.isArray(payload) ? payload : payload.results || []

    // Filter out the current user from the results
    const filteredData = data.filter(user => user.username !== session.user?.username)

    users.value = filteredData.map(mapUser)
    if (!Array.isArray(payload)) {
      nextUrl.value = payload.next || ''
      prevUrl.value = payload.previous || ''
      total.value = payload.count || 0
      const inferred = getPageFromUrl(input)
      if (inferred) page.value = inferred
    }
    if (users.value.length === 0) {
      errorMsg.value = 'No users available yet.'
    }
    showNotification(`Loaded ${users.value.length} users`, 'success', 3000)
  } catch (e) {
    errorMsg.value = 'Could not load users. Please retry.'
    showNotification('Failed to load users', 'error', 5000)
  } finally {
    loading.value = false
  }
}

async function searchUsers() {
  if (searchQuery.value.trim()) {
    try {
      const payload = await json(`/api/users/?search=${encodeURIComponent(searchQuery.value.trim())}`)
      const data = Array.isArray(payload) ? payload : payload.results || []
      users.value = data.map(mapUser)
      nextUrl.value = payload.next || ''
      prevUrl.value = payload.previous || ''
      total.value = payload.count || 0
      page.value = 1
      showNotification(`Found ${users.value.length} users matching "${searchQuery.value}"`, 'success', 4000)
    } catch (e) {
      errorMsg.value = 'Search failed.'
      showNotification('Search failed', 'error', 5000)
    }
  } else {
    fetchData()
  }
}

function handleSearchInput() {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  searchTimeout.value = setTimeout(() => {
    searchUsers()
  }, 500)
}

function nextPage() {
  if (nextUrl.value) fetchData(nextUrl.value)
}
function prevPage() {
  if (prevUrl.value) fetchData(prevUrl.value)
}

function clearFilters() {
  filterPremium.value = false
  filterPrivate.value = false
  searchQuery.value = ''
  fetchData()
  showNotification('Filters cleared', 'info', 3000)
}

const filteredUsers = computed(() => {
  let filtered = users.value

  if (filterPremium.value) {
    filtered = filtered.filter(u => u.is_premium)
  }

  if (filterPrivate.value) {
    filtered = filtered.filter(u => u.is_private)
  }

  return filtered
})

onMounted(() => {
  fetchData()
  const onVis = () => { if (document.visibilityState === 'visible') fetchData(`/api/users/?page=${page.value}`) }
  document.addEventListener('visibilitychange', onVis)
  onUnmounted(() => document.removeEventListener('visibilitychange', onVis))
})

const title = computed(() => 'All users')
</script>

<template>
  <div class="container">
    <Breadcrumbs />

    <div style="display:flex; align-items:center; gap:8px; margin:0 0 16px;">
      <h2 style="margin:0; font-size:22px; font-weight:700;">Users</h2>
    </div>

    <!-- Filters Panel -->
    <div v-if="showFilters" class="card" style="padding:16px; margin-bottom:16px; background:var(--c-surface-2); border:1px solid var(--c-border);">
      <div style="display:flex; align-items:center; gap:16px; flex-wrap:wrap;">
        <label style="display:flex; align-items:center; gap:8px; cursor:pointer;">
          <input type="checkbox" v-model="filterPremium" style="width:16px; height:16px;" />
          <span style="font-size:13px; color:var(--c-text);">⭐ Premium users only</span>
        </label>
        <label style="display:flex; align-items:center; gap:8px; cursor:pointer;">
          <input type="checkbox" v-model="filterPrivate" style="width:16px; height:16px;" />
          <span style="font-size:13px; color:var(--c-text);">🔒 Private accounts only</span>
        </label>
        <button @click="clearFilters" style="padding:6px 12px; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:8px; font-size:12px; cursor:pointer;">Clear Filters</button>
      </div>
    </div>

    <div v-if="loading" class="grid grid-cols-responsive" style="gap:12px;">
      <UserCardSkeleton v-for="i in 8" :key="i" />
    </div>
    <div v-else-if="errorMsg" class="card" style="padding:16px; color:var(--c-text-muted); display:flex; align-items:center; gap:12px;">
      <span style="flex:1;">{{ errorMsg }}</span>
      <button @click="fetchData()` + '`' + `" style="border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:10px; padding:8px 12px; cursor:pointer; font-size:13px;">Retry</button>
    </div>
    <div v-else-if="filteredUsers.length === 0" class="card" style="padding:32px; text-align:center; color:var(--c-text-muted);">
      <div style="font-size:48px; margin-bottom:16px;">👥</div>
      <div style="font-size:18px; font-weight:600; margin-bottom:8px;">No users found</div>
      <div>{{ searchQuery || filterPremium || filterPrivate ? 'Try adjusting your filters or search terms' : 'No users available yet' }}</div>
    </div>
    <div v-else class="grid grid-cols-responsive" data-testid="users-grid">
      <UserCard v-for="u in filteredUsers" :key="u.id" :user="u" />
    </div>

    <div style="display:flex; gap:8px; align-items:center; justify-content:space-between; margin-top:16px;">
      <div style="color:var(--c-text-muted); font-size:13px;">
        Showing {{ filteredUsers.length }} of {{ total }} users
        <span v-if="filterPremium || filterPrivate || searchQuery" style="color:var(--c-accent);">(filtered)</span>
      </div>
      <div style="display:flex; gap:8px;">
        <button :disabled="!prevUrl || loading" @click="prevPage" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:6px 10px; cursor:pointer; font-size:13px; opacity: var(--opacity, 1);" :style="{ '--opacity': (!prevUrl || loading) ? 0.6 : 1 }">Prev</button>
        <div style="font-size:13px; color:var(--c-text-muted);">Page {{ page }}</div>
        <button :disabled="!nextUrl || loading" @click="nextPage" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:6px 10px; cursor:pointer; font-size:13px; opacity: var(--opacity, 1);" :style="{ '--opacity': (!nextUrl || loading) ? 0.6 : 1 }">Next</button>
      </div>
    </div>
  </div>
</template>
