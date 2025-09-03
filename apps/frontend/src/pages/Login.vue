<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'

const router = useRouter()
const session = useSessionStore()
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
    await session.login({ username: username.value.trim(), password: password.value, rememberMe: rememberMe.value })
    await session.fetchMe()
    router.push('/feed')
  } catch (err) {
    console.error('Login error:', err)
    error.value = 'Login failed. Please check your credentials.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-form-container">
    <h2 class="login-title">Sign In</h2>
    <p class="login-description">Welcome back! Please sign in to your account.</p>

    <form class="login-form" @submit="submit">
      <div class="form-group">
        <label for="username" class="form-label">Username</label>
        <input
          id="username"
          v-model="username"
          type="text"
          class="form-input"
          placeholder="Enter your username"
          required
          :disabled="loading"
        />
      </div>

      <div class="form-group">
        <label for="password" class="form-label">Password</label>
        <input
          id="password"
          v-model="password"
          type="password"
          class="form-input"
          placeholder="Enter your password"
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
          <span class="checkbox-text">Remember me</span>
        </label>
      </div>

      <button
        type="submit"
        class="login-button"
        :disabled="loading"
      >
        <span v-if="loading" class="loading-spinner"></span>
        <span v-else>Sign In</span>
      </button>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </form>

    <div class="login-footer">
      <p class="footer-text">
        Don't have an account?
        <router-link to="/auth/register" class="footer-link">Sign up</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.login-form-container {
  width: 100%;
}

.login-title {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.login-description {
  color: #6b7280;
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
  color: #374151;
  text-align: left;
}

.form-input {
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 14px;
  transition: all 0.2s ease;
  background: #f9fafb;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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
  accent-color: #667eea;
}

.checkbox-text {
  font-size: 14px;
  color: #6b7280;
}

.login-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
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
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
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
  border-top: 2px solid white;
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
  border-top: 1px solid #e5e7eb;
}

.footer-text {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
}

.footer-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.footer-link:hover {
  text-decoration: underline;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Dark theme support */
@media (prefers-color-scheme: dark) {
  .login-title {
    color: white;
  }

  .form-label {
    color: #d1d5db;
  }

  .form-input {
    background: #374151;
    border-color: #4b5563;
    color: white;
  }

  .form-input:focus {
    background: #4b5563;
  }

  .checkbox-text {
    color: #d1d5db;
  }

  .login-description {
    color: #9ca3af;
  }

  .footer-text {
    color: #9ca3af;
  }

  .login-footer {
    border-top-color: #4b5563;
  }
}
</style>
