<script setup>
import { ref, onMounted } from 'vue'
import { json } from '@/lib/http'
import { useSessionStore } from '@/stores/session'

const session = useSessionStore()

const changingPass = ref(false)
const deleting = ref(false)
const message = ref('')
const messageType = ref('') // 'success' | 'error'

const old_password = ref('')
const new_password = ref('')
const confirm_password = ref('')

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

onMounted(() => {
  // loadMe() // Removed as per edit hint
})
</script>

<template>
  <div class="container">
    <div style="display:flex; align-items:center; gap:8px; margin:0 0 24px;">
      <h2 style="margin:0; font-size:22px; font-weight:700;">Account Settings</h2>
      <div v-if="message" style="margin-left:auto; padding:8px 16px; border-radius:8px; font-size:13px; font-weight:500;" :style="messageType === 'success' ? 'background:#dcfce7; color:#166534; border:1px solid #bbf7d0;' : 'background:#fee2e2; color:#b91c1c; border:1px solid #fecaca;'">
        {{ message }}
      </div>
    </div>

    <div class="grid" style="grid-template-columns: 1fr; gap:24px;">
      <!-- Password Change -->
      <div class="card" style="padding:24px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">
          <div style="width:48px; height:48px; background:linear-gradient(135deg,#ff4db0,#4db2ff); border-radius:12px; display:grid; place-items:center; color:#fff; font-weight:600; font-size:20px;">
            🔐
          </div>
          <div>
            <h3 style="margin:0; font-size:18px; font-weight:600;">Change Password</h3>
            <p style="margin:4px 0 0; color:var(--c-text-muted); font-size:14px;">Update your account password</p>
          </div>
        </div>

        <form @submit.prevent="changePassword" style="display:grid; gap:16px;">
          <label style="display:grid; gap:6px;">
            <span style="font-size:13px; color:var(--c-text-muted); font-weight:500;">Current Password *</span>
            <input v-model="old_password" type="password" required style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px;" />
          </label>

          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
            <label style="display:grid; gap:6px;">
              <span style="font-size:13px; color:var(--c-text-muted); font-weight:500;">New Password *</span>
              <input v-model="new_password" type="password" required style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px;" />
            </label>
            <label style="display:grid; gap:6px;">
              <span style="font-size:13px; color:var(--c-text-muted); font-weight:500;">Confirm New Password *</span>
              <input v-model="confirm_password" type="password" required style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px;" />
            </label>
          </div>

          <div style="display:flex; gap:12px; justify-content:flex-end;">
            <button type="submit" :disabled="changingPass || !old_password || !new_password || !confirm_password" style="border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:10px; padding:10px 20px; cursor:pointer; font-size:14px; font-weight:500;">
              {{ changingPass ? 'Changing...' : 'Change Password' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Account Deactivation -->
      <div class="card" style="padding:24px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">
          <div style="width:48px; height:48px; background:linear-gradient(135deg,#ef4444,#dc2626); border-radius:12px; display:grid; place-items:center; color:#fff; font-weight:600; font-size:20px;">
            ⚠️
          </div>
          <div>
            <h3 style="margin:0; font-size:18px; font-weight:600;">Account Deactivation</h3>
            <p style="margin:4px 0 0; color:var(--c-text-muted); font-size:14px;">Deactivate your account (reversible)</p>
          </div>
        </div>

        <div style="display:grid; gap:16px;">
          <p style="color:var(--c-text-muted); font-size:14px; line-height:1.5;">
            Deactivating your account will hide your profile and content from other users.
            You can reactivate it anytime by logging back in.
          </p>

          <div style="display:flex; gap:12px; justify-content:flex-end;">
            <button @click="softDelete" :disabled="deleting" style="border:1px solid #ef4444; background:#ef4444; color:white; border-radius:10px; padding:10px 20px; cursor:pointer; font-size:14px; font-weight:500;">
              {{ deleting ? 'Deactivating...' : 'Deactivate Account' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
