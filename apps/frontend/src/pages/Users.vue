<script setup>
import { ref, onMounted, computed } from 'vue'
import UserCard from '@/components/UserCard.vue'
import UserCardSkeleton from '@/components/UserCardSkeleton.vue'

const loading = ref(true)
const users = ref([])

onMounted(async () => {
  try {
    const res = await fetch('http://127.0.0.1:8000/api/users/')
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
  } finally {
    loading.value = false
  }
})

const title = computed(() => 'All users')
</script>

<template>
  <div class="container">
    <h2 style="margin:0 0 16px; font-size:22px; font-weight:700;">{{ title }}</h2>

    <div class="grid grid-cols-responsive" data-testid="users-grid">
      <template v-if="loading">
        <UserCardSkeleton v-for="n in 9" :key="n" />
      </template>
      <template v-else>
        <UserCard v-for="u in users" :key="u.id" :user="u" />
      </template>
    </div>
  </div>
</template>


