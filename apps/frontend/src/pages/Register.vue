<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { json } from '@/lib/http'

const router = useRouter()
const session = useSessionStore()
const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')

async function submit(e) {
  e.preventDefault()
  error.value = ''
  try {
    await session.register({ username: username.value, password: password.value, email: email.value })
    await session.login({ username: username.value, password: password.value, rememberMe: true })
    await session.fetchMe()
    router.push('/users')
  } catch (err) {
    error.value = 'Register failed'
  }
}
</script>

<template>
  <div class="container" style="max-width:420px;">
    <h2 style="margin:0 0 16px; font-size:22px; font-weight:700;">Register</h2>
    <form class="card" style="padding:16px; display:grid; gap:12px;" @submit="submit">
      <input v-model="username" placeholder="Username" required style="padding:10px; border:1px solid var(--c-border); border-radius:10px; background:var(--c-surface); color:var(--c-text);" />
      <input v-model="email" placeholder="Email" type="email" style="padding:10px; border:1px solid var(--c-border); border-radius:10px; background:var(--c-surface); color:var(--c-text);" />
      <input v-model="password" placeholder="Password" type="password" required style="padding:10px; border:1px solid var(--c-border); border-radius:10px; background:var(--c-surface); color:var(--c-text);" />
      <button type="submit" class="btn-prim" style="padding:10px 12px; border-radius:10px;">Create account</button>
      <div v-if="error" style="color:#f87171; font-size:13px;">{{ error }}</div>
    </form>
  </div>
  </template>

