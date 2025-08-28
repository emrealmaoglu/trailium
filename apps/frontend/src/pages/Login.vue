<script setup>
/**
 * Giriş sayfası: i18n ile iki dilli metinler.
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const session = useSessionStore()
const { t } = useI18n()
const username = ref('')
const password = ref('')
const rememberMe = ref(true)
const error = ref('')
const loading = ref(false)

async function submit(e) {
  e.preventDefault()
  error.value = ''
  loading.value = true

  try {
    await session.login({ username: username.value, password: password.value, rememberMe: rememberMe.value })
    await session.fetchMe()
    router.push('/users')
  } catch (err) {
    console.error('Login error:', err)
    error.value = 'Login failed. Please check your credentials.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="login-form-container card">
      <h2 class="login-title">{{ t('auth.login') }}</h2>
      <p class="login-description">{{ t('auth.welcomeBack') }}</p>

      <form class="login-form" @submit="submit">
      <div class="form-group">
        <label for="username" class="form-label">{{ t('auth.username') }}</label>
        <input
          id="username"
          v-model="username"
          type="text"
          class="form-input"
          placeholder="{{ t('auth.username') }}"
          required
          :disabled="loading"
        />
      </div>

      <div class="form-group">
        <label for="password" class="form-label">{{ t('auth.password') }}</label>
        <input
          id="password"
          v-model="password"
          type="password"
          class="form-input"
          placeholder="{{ t('auth.password') }}"
          required
          :disabled="loading"
        />
      </div>

      <div class="form-options">
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="rememberMe"
            class="checkbox-input"
            :disabled="loading"
          />
          <span class="checkbox-text">{{ t('auth.rememberMe') }}</span>
        </label>
      </div>

        <button
          type="submit"
          class="login-button"
          :disabled="loading"
        >
          <span v-if="loading" class="loading-spinner"></span>
          <span v-else>{{ t('auth.signInCta') }}</span>
        </button>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </form>

      <div class="login-footer">
        <p class="footer-text">
          {{ t('auth.haveNoAccount') }}
          <router-link to="/register" class="footer-link">{{ t('auth.register') }}</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: calc(100vh - 64px);
  display: grid;
  place-items: center;
  padding: 24px;
  background: var(--c-bg);
}

.login-form-container {
  width: 100%;
  max-width: 420px;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.06);
}

.login-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--c-text);
  margin: 0 0 8px 0;
}

.login-description {
  color: var(--c-text-muted);
  font-size: 14px;
  margin: 0 0 24px 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--c-text);
  text-align: left;
}

.form-input {
  padding: 12px 16px;
  border: 2px solid var(--c-border);
  border-radius: 12px;
  font-size: 14px;
  transition: all 0.2s ease;
  background: var(--c-surface-2);
  color: var(--c-text);
}

.form-input:focus {
  outline: none;
  border-color: var(--c-accent);
  background: var(--c-surface);
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.15);
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-input {
  width: 16px;
  height: 16px;
  accent-color: var(--c-accent);
}

.checkbox-text {
  font-size: 14px;
  color: var(--c-text-muted);
}

.login-button {
  background: var(--c-accent);
  color: white;
  border: 2px solid var(--c-accent);
  padding: 14px 24px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.login-button:hover:not(:disabled) {
  background: var(--c-accent-hover);
  border-color: var(--c-accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.login-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.error-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--c-border);
}

.footer-text {
  color: var(--c-text-muted);
  font-size: 14px;
  margin: 0;
}

.footer-link {
  color: var(--c-accent);
  text-decoration: none;
  font-weight: 500;
}

.footer-link:hover {
  text-decoration: underline;
  color: var(--c-accent-hover);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Responsive */
@media (max-width: 480px) {
  .login-form-container { padding: 20px; border-radius: 14px; }
}
</style>
