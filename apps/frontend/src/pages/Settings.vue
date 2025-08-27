<script setup>
import { ref } from 'vue'
import { json } from '@/lib/http'
import { useSessionStore } from '@/stores/session'
import FollowRequests from '@/components/FollowRequests.vue'

const session = useSessionStore()

const changingPass = ref(false)
const deleting = ref(false)
const message = ref('')
const messageType = ref('') // 'success' | 'error'

const old_password = ref('')
const new_password = ref('')
const confirm_password = ref('')
const isPrivate = ref(false)
const profilePrivacy = ref('public')



async function changePassword() {
  if (!old_password.value || !new_password.value || !confirm_password.value) {
    showMessage('All password fields are required', 'error')
    return
  }

  if (new_password.value !== confirm_password.value) {
    showMessage('New passwords do not match', 'error')
    return
  }

  if (new_password.value.length < 8) {
    showMessage('New password must be at least 8 characters', 'error')
    return
  }

  changingPass.value = true
  try {
    await json('/api/auth/change-password/', {
      method: 'POST',
      body: JSON.stringify({
        old_password: old_password.value,
        new_password: new_password.value
      })
    })
    old_password.value = ''
    new_password.value = ''
    confirm_password.value = ''
    showMessage('Password changed successfully! Please re-login.', 'success')
    await session.logout()
  } catch (e) {
    showMessage('Password change failed. Please check your old password.', 'error')
  } finally {
    changingPass.value = false
  }
}

async function softDelete() {
  if (!confirm('Are you sure you want to deactivate your account? This action cannot be undone.')) return
  deleting.value = true
  try {
    await json('/api/users/me/', { method: 'DELETE' })
    showMessage('Account deactivated successfully.', 'success')
    await session.logout()
  } catch (e) {
    showMessage('Could not deactivate account. Please try again.', 'error')
  } finally {
    deleting.value = false
  }
}

function showMessage(msg, type = 'success') {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
    messageType.value = ''
  }, 5000)
}
</script>

<template>
  <div class="container">
    <div class="page-header">
      <h2 class="page-title">Account Settings</h2>
      <div v-if="message" class="message" :class="messageType">
        {{ message }}
      </div>
    </div>

    <div class="settings-grid">

      <!-- Follow Requests -->
      <div class="card">
        <div class="card-header">
          <div class="card-icon follow-icon">
            👥
          </div>
          <div>
            <h3 class="card-title">Follow Requests</h3>
            <p class="card-subtitle">Manage incoming follow requests</p>
          </div>
        </div>

        <FollowRequests />
      </div>

      <!-- Privacy Settings -->
      <div class="card">
        <div class="card-header">
          <div class="card-icon privacy-icon">
            🔒
          </div>
          <div>
            <h3 class="card-title">Privacy Settings</h3>
            <p class="card-subtitle">Control who can see your profile and content</p>
          </div>
        </div>

        <div class="form-section">
          <label class="form-label">
            <span class="label-text">Profile Privacy</span>
            <select v-model="profilePrivacy" class="form-select">
              <option value="public">Public - Anyone can see your profile</option>
              <option value="followers">Followers Only - Only followers can see your profile</option>
              <option value="private">Private - Only you can see your profile</option>
            </select>
          </label>

          <label class="checkbox-label">
            <input type="checkbox" v-model="isPrivate" class="checkbox-input" />
            <span class="checkbox-text">Make account private (requires approval for new followers)</span>
          </label>

          <div class="info-box">
            <div class="info-content">
              <strong>Privacy notes:</strong>
              <ul class="info-list">
                <li>Private accounts require approval for new followers</li>
                <li>Profile privacy affects who can see your posts and information</li>
                <li>You can change these settings at any time</li>
              </ul>
            </div>
          </div>

          <div class="form-actions">
            <button class="btn-primary">
              Save Privacy Settings
            </button>
          </div>
        </div>
      </div>

      <!-- Password Change -->
      <div class="card">
        <div class="card-header">
          <div class="card-icon password-icon">
            🔐
          </div>
          <div>
            <h3 class="card-title">Change Password</h3>
            <p class="card-subtitle">Update your account password</p>
          </div>
        </div>

        <form @submit.prevent="changePassword" class="form-section">
          <label class="form-label">
            <span class="label-text">Current Password *</span>
            <input v-model="old_password" type="password" required class="form-input" />
          </label>

          <div class="form-row">
            <label class="form-label">
              <span class="label-text">New Password *</span>
              <input v-model="new_password" type="password" required minlength="8" class="form-input" />
            </label>
            <label class="form-label">
              <span class="label-text">Confirm Password *</span>
              <input v-model="confirm_password" type="password" required minlength="8" class="form-input" />
            </label>
          </div>

          <div class="info-box">
            <div class="info-content">
              <strong>Password requirements:</strong>
              <ul class="info-list">
                <li>At least 8 characters long</li>
                <li>Use a mix of letters, numbers, and symbols</li>
              </ul>
            </div>
          </div>

          <div class="form-actions">
            <button :disabled="changingPass || !old_password || !new_password || !confirm_password" class="btn-primary">
              {{ changingPass ? 'Changing…' : 'Change Password' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Danger Zone -->
      <div class="card danger-card">
        <div class="card-header">
          <div class="card-icon danger-icon">
            ⚠️
          </div>
          <div>
            <h3 class="card-title danger-title">Danger Zone</h3>
            <p class="card-subtitle">Irreversible and destructive actions</p>
          </div>
        </div>

        <div class="danger-content">
          <div class="danger-title-small">Deactivate Account</div>
          <div class="danger-description">
            This will deactivate your account and hide your profile. You can reactivate by logging in again.
          </div>
          <button :disabled="deleting" @click="softDelete" class="btn-danger">
            {{ deleting ? 'Processing…' : 'Deactivate Account' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Layout */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.settings-grid {
  grid-template-columns: 1fr;
  gap: 24px;
  display: grid;
}

.card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.danger-card {
  border: 2px solid #fecaca;
}

/* Page Header */
.page-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 24px;
}

.page-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
}

.message {
  margin-left: auto;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
}

.message.success {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.message.error {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

/* Card Header */
.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 600;
  font-size: 20px;
}

.follow-icon {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
}

.privacy-icon {
  background: linear-gradient(135deg, #a855f7, #ec4899);
}

.password-icon {
  background: linear-gradient(135deg, #4db2ff, #4dffb2);
}

.danger-icon {
  background: #fee2e2;
  color: #b91c1c;
}

.card-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.danger-title {
  color: #b91c1c;
}

.card-subtitle {
  margin: 4px 0 0;
  color: var(--c-text-muted);
  font-size: 14px;
}

/* Form Layout */
.form-section {
  display: grid;
  gap: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-label {
  display: grid;
  gap: 6px;
}

.label-text {
  font-size: 13px;
  color: var(--c-text-muted);
  font-weight: 500;
}

/* Form Inputs */
.form-input,
.form-select {
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-text);
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--c-accent);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* Checkbox */
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 12px;
}

.checkbox-input {
  width: 18px;
  height: 18px;
}

.checkbox-text {
  font-size: 14px;
  color: var(--c-text);
}

/* Info Boxes */
.info-box {
  padding: 12px;
  border: 1px solid var(--c-border);
  border-radius: 10px;
  background: var(--c-surface-2);
}

.info-content {
  font-size: 12px;
  color: var(--c-text-muted);
}

.info-list {
  margin: 8px 0 0 16px;
  padding: 0;
}

/* Danger Zone */
.danger-content {
  padding: 16px;
  border: 1px solid #fecaca;
  border-radius: 10px;
  background: #fef2f2;
}

.danger-title-small {
  font-weight: 500;
  color: #b91c1c;
  margin-bottom: 8px;
}

.danger-description {
  font-size: 13px;
  color: #b91c1c;
  margin-bottom: 16px;
}

/* Buttons */
.form-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-primary {
  border: 1px solid var(--c-accent);
  background: var(--c-accent);
  color: white;
  border-radius: 10px;
  padding: 10px 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-danger {
  border: 1px solid #fecaca;
  background: #fee2e2;
  color: #b91c1c;
  border-radius: 10px;
  padding: 10px 16px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-danger:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive Design */
@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .card {
    padding: 16px;
  }

  .settings-grid {
    gap: 16px;
  }
}
</style>
