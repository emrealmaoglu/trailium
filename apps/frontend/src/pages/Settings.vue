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
const profilePhoto = ref(null)
const isPrivate = ref(false)
const profilePrivacy = ref('public')

async function uploadProfilePhoto() {
  if (!profilePhoto.value) return

  try {
    const formData = new FormData()
    formData.append('avatar', profilePhoto.value)

    const response = await json('/api/users/me/', {
      method: 'PATCH',
      body: formData,
      headers: {} // Let browser set content-type for FormData
    })

    showMessage('Profile photo updated successfully!', 'success')
    profilePhoto.value = null

    // Update session user avatar
    if (session.user) {
      session.user.avatar = response.avatar
    }
  } catch (error) {
    showMessage('Failed to upload profile photo. Please try again.', 'error')
  }
}

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
    <div style="display:flex; align-items:center; gap:8px; margin:0 0 24px;">
      <h2 style="margin:0; font-size:22px; font-weight:700;">Account Settings</h2>
      <div v-if="message" style="margin-left:auto; padding:8px 16px; border-radius:8px; font-size:13px; font-weight:500;" :style="messageType === 'success' ? 'background:#dcfce7; color:#166534; border:1px solid #bbf7d0;' : 'background:#fee2e2; color:#b91c1c; border:1px solid #fecaca;'">
        {{ message }}
      </div>
    </div>

    <div class="grid" style="grid-template-columns: 1fr; gap:24px;">
      <!-- Profile Photo Upload -->
      <div class="card" style="padding:24px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">
          <div style="width:48px; height:48px; background:linear-gradient(135deg,#ff6b6b,#4ecdc4); border-radius:12px; display:grid; place-items:center; color:#fff; font-weight:600; font-size:20px;">
            📸
          </div>
          <div>
            <h3 style="margin:0; font-size:18px; font-weight:600;">Profile Photo</h3>
            <p style="margin:4px 0 0; color:var(--c-text-muted); font-size:14px;">Upload or change your profile picture</p>
          </div>
        </div>

        <div style="display:grid; gap:16px;">
          <div style="display:flex; align-items:center; gap:16px;">
            <div style="width:80px; height:80px; border-radius:50%; background:var(--c-surface-2); border:2px solid var(--c-border); display:grid; place-items:center; font-size:32px;">
              👤
            </div>
            <div style="flex:1;">
              <input type="file" accept="image/*" @change="profilePhoto = $event.target.files[0]" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px; width:100%;" />
              <p style="margin:8px 0 0; font-size:12px; color:var(--c-text-muted);">Supported formats: JPG, PNG, GIF (max 5MB)</p>
            </div>
          </div>

          <div style="display:flex; justify-content:flex-end;">
            <button @click="uploadProfilePhoto" :disabled="!profilePhoto" style="border:1px solid var(--c-accent); background:var(--c-accent); color:var(--c-text); border-radius:10px; padding:10px 20px; cursor:pointer; font-size:14px; font-weight:500;">
              Upload Photo
            </button>
          </div>
        </div>
      </div>

      <!-- Follow Requests -->
      <div class="card" style="padding:24px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">
          <div style="width:48px; height:48px; background:linear-gradient(135deg,#3b82f6,#8b5cf6); border-radius:12px; display:grid; place-items:center; color:#fff; font-weight:600; font-size:20px;">
            👥
          </div>
          <div>
            <h3 style="margin:0; font-size:18px; font-weight:600;">Follow Requests</h3>
            <p style="margin:4px 0 0; color:var(--c-text-muted); font-size:14px;">Manage incoming follow requests</p>
          </div>
        </div>

        <FollowRequests />
      </div>

      <!-- Privacy Settings -->
      <div class="card" style="padding:24px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">
          <div style="width:48px; height:48px; background:linear-gradient(135deg,#a855f7,#ec4899); border-radius:12px; display:grid; place-items:center; color:#fff; font-weight:600; font-size:20px;">
            🔒
          </div>
          <div>
            <h3 style="margin:0; font-size:18px; font-weight:600;">Privacy Settings</h3>
            <p style="margin:4px 0 0; color:var(--c-text-muted); font-size:14px;">Control who can see your profile and content</p>
          </div>
        </div>

        <div style="display:grid; gap:16px;">
          <label style="display:grid; gap:6px;">
            <span style="font-size:13px; color:var(--c-text-muted); font-weight:500;">Profile Privacy</span>
            <select v-model="profilePrivacy" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px;">
              <option value="public">Public - Anyone can see your profile</option>
              <option value="followers">Followers Only - Only followers can see your profile</option>
              <option value="private">Private - Only you can see your profile</option>
            </select>
          </label>

          <label style="display:flex; align-items:center; gap:12px;">
            <input type="checkbox" v-model="isPrivate" style="width:18px; height:18px;" />
            <span style="font-size:14px; color:var(--c-text);">Make account private (requires approval for new followers)</span>
          </label>

          <div style="padding:12px; border:1px solid var(--c-border); border-radius:10px; background:var(--c-surface-2);">
            <div style="font-size:12px; color:var(--c-text-muted);">
              <strong>Privacy notes:</strong>
              <ul style="margin:8px 0 0 16px; padding:0;">
                <li>Private accounts require approval for new followers</li>
                <li>Profile privacy affects who can see your posts and information</li>
                <li>You can change these settings at any time</li>
              </ul>
            </div>
          </div>

          <div style="display:flex; justify-content:flex-end;">
            <button style="border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:10px; padding:10px 20px; cursor:pointer; font-size:14px; font-weight:500;">
              Save Privacy Settings
            </button>
          </div>
        </div>
      </div>

      <!-- Password Change -->
      <div class="card" style="padding:24px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">
          <div style="width:48px; height:48px; background:linear-gradient(135deg,#4db2ff,#4dffb2); border-radius:12px; display:grid; place-items:center; color:#fff; font-weight:600; font-size:20px;">
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
              <input v-model="new_password" type="password" required minlength="8" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px;" />
            </label>
            <label style="display:grid; gap:6px;">
              <span style="font-size:13px; color:var(--c-text-muted); font-weight:500;">Confirm Password *</span>
              <input v-model="confirm_password" type="password" required minlength="8" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px;" />
            </label>
          </div>

          <div style="padding:12px; border:1px solid var(--c-border); border-radius:10px; background:var(--c-surface-2);">
            <div style="font-size:12px; color:var(--c-text-muted);">
              <strong>Password requirements:</strong>
              <ul style="margin:8px 0 0 16px; padding:0;">
                <li>At least 8 characters long</li>
                <li>Use a mix of letters, numbers, and symbols</li>
              </ul>
            </div>
          </div>

          <div style="display:flex; justify-content:flex-end;">
            <button :disabled="changingPass || !old_password || !new_password || !confirm_password" style="border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:10px; padding:10px 20px; cursor:pointer; font-size:14px; font-weight:500;">
              {{ changingPass ? 'Changing…' : 'Change Password' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Danger Zone -->
      <div class="card" style="padding:24px; border:2px solid #fecaca;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">
          <div style="width:48px; height:48px; background:#fee2e2; border-radius:12px; display:grid; place-items:center; color:#b91c1c; font-weight:600; font-size:20px;">
            ⚠️
          </div>
          <div>
            <h3 style="margin:0; font-size:18px; font-weight:600; color:#b91c1c;">Danger Zone</h3>
            <p style="margin:4px 0 0; color:var(--c-text-muted); font-size:14px;">Irreversible and destructive actions</p>
          </div>
        </div>

        <div style="padding:16px; border:1px solid #fecaca; border-radius:10px; background:#fef2f2;">
          <div style="font-weight:500; color:#b91c1c; margin-bottom:8px;">Deactivate Account</div>
          <div style="font-size:13px; color:#b91c1c; margin-bottom:16px;">
            This will deactivate your account and hide your profile. You can reactivate by logging in again.
          </div>
          <button :disabled="deleting" @click="softDelete" style="border:1px solid #fecaca; background:#fee2e2; color:#b91c1c; border-radius:10px; padding:10px 16px; cursor:pointer; font-size:14px; font-weight:500;">
            {{ deleting ? 'Processing…' : 'Deactivate Account' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
