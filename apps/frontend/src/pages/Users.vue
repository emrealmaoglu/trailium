<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { json } from '@/lib/http'
import UserCard from '@/components/UserCard.vue'
import UserCardSkeleton from '@/components/UserCardSkeleton.vue'

const loading = ref(true)
const users = ref([])
const errorMsg = ref('')

async function fetchData() {
  loading.value = true
  errorMsg.value = ''
  try {
    const payload = await json('/api/users/')
    const data = Array.isArray(payload) ? payload : payload.results || []
    users.value = data.map(u => ({
      id: u.id,
      name: u.name,
      email: u.email,
      phone: u.phone,
      addressText: u.address || '',
      companyName: u.company || '',
      website: (u.website || '').replace(/^https?:\/\//,'')
    }))
    if (users.value.length === 0) {
      errorMsg.value = 'No users available yet.'
    }
  } catch (e) {
    errorMsg.value = 'Could not load users. Please retry.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
  const onVis = () => { if (document.visibilityState === 'visible') fetchData() }
  document.addEventListener('visibilitychange', onVis)
  onUnmounted(() => document.removeEventListener('visibilitychange', onVis))
})

const title = computed(() => 'All users')
</script>

<template>
  <div class="container">
    <div style="display:flex; align-items:center; gap:8px; margin:0 0 16px;">
      <h2 style="margin:0; font-size:22px; font-weight:700;">{{ title }}</h2>
      <button @click="fetchData" style="margin-left:auto; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:6px 10px; cursor:pointer; font-size:13px;">Refresh</button>
    </div>

    <div v-if="errorMsg && !loading" style="padding:16px; color:var(--c-text-muted);">{{ errorMsg }}</div>
    <div v-else class="grid grid-cols-responsive" data-testid="users-grid">
      <template v-if="loading">
        <UserCardSkeleton v-for="n in 9" :key="n" />
      </template>
      <template v-else>
        <UserCard v-for="u in users" :key="u.id" :user="u" />
      </template>
    </div>
  </div>
</template>


