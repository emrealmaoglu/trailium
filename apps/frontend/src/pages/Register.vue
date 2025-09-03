<script setup>
/**
 * Kayıt sayfası: i18n ile iki dilli metinler.
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { json } from '@/lib/http'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const session = useSessionStore()
const { t } = useI18n()
const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit(e) {
  e.preventDefault()
  error.value = ''
  try {
    loading.value = true
    await session.register({ username: username.value, password: password.value, email: email.value })
    await session.login({ username: username.value, password: password.value, rememberMe: true })
    await session.fetchMe()
    router.push('/users')
  } catch (err) {
    const msg = (err && err.message) ? err.message : 'Register failed'
    error.value = msg
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="register-card">
      <h2 class="title">{{ t('auth.register') }}</h2>
      <form class="form" @submit="submit">
        <input v-model="username" :placeholder="t('auth.username')" required class="input" />
        <input v-model="email" :placeholder="t('auth.email')" type="email" class="input" />
        <input v-model="password" :placeholder="t('auth.password')" type="password" required class="input" />
        <button type="submit" class="btn" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>{{ t('auth.createAccountCta') }}</span>
        </button>
        <div v-if="error" class="error">{{ error }}</div>
      </form>
    </div>
  </div>
  </template>
<style scoped>
.auth-page { min-height: calc(100vh - 64px); display: grid; place-items: center; padding: 24px; background: var(--c-bg); }
.register-card { width: 100%; max-width: 420px; background: var(--c-surface); border: 1px solid var(--c-border); border-radius: 16px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,.06); }
.title { margin: 0 0 16px; font-size: 22px; font-weight: 700; color: var(--c-text); }
.form { display: grid; gap: 12px; }
.input { padding: 12px 14px; border: 2px solid var(--c-border); border-radius: 12px; background: var(--c-surface-2); color: var(--c-text); font-size: 14px; }
.input:focus { outline: none; border-color: var(--c-accent); background: var(--c-surface); box-shadow: 0 0 0 3px rgba(0,123,255,.15); }
.btn { padding: 12px 14px; border-radius: 12px; background: var(--c-accent); color: #fff; border: 2px solid var(--c-accent); font-weight: 600; cursor: pointer; transition: .2s; display: inline-flex; align-items: center; justify-content: center; gap: 8px; }
.btn:hover:enabled { background: var(--c-accent-hover); border-color: var(--c-accent-hover); transform: translateY(-1px); }
.btn:disabled { opacity: .7; cursor: not-allowed; transform: none; }
.spinner { width: 16px; height: 16px; border: 2px solid transparent; border-top: 2px solid #fff; border-radius: 50%; animation: spin 1s linear infinite; }
.error { color: #dc2626; font-size: 13px; text-align: center; background: #fef2f2; border: 1px solid #fecaca; padding: 8px 10px; border-radius: 8px; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
