<script setup>
import { ref, onMounted, computed } from 'vue'
import UserCard from '@/components/UserCard.vue'
import UserCardSkeleton from '@/components/UserCardSkeleton.vue'

const loading = ref(true)
const users = ref([])
const errorMsg = ref('')

onMounted(async () => {
  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
  try {
    const res = await fetch(`${API_BASE}/api/users/`)
    if (!res.ok) throw new Error(`Request failed: ${res.status}`)
    const payload = await res.json()
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
})

const title = computed(() => 'All users')
</script>

<template>
  <div class="container">
    <h2 style="margin:0 0 16px; font-size:22px; font-weight:700;">{{ title }}</h2>

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


