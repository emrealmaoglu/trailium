<script setup>
import { ref, onMounted } from 'vue'
import { json } from '@/lib/http'
import { useSessionStore } from '@/stores/session'

const session = useSessionStore()

const savingProfile = ref(false)
const message = ref('')
const messageType = ref('') // 'success' | 'error'

const profile = ref({
  username: '',
  email: '',
  full_name: '',
  avatar: '',
  gender: '',
  phone: '',
  address: '',
  about: '',
  birth_date: '',
  website: '',
  location: '',
})

const genderOptions = [
  { value: '', label: 'Prefer not to say' },
  { value: 'M', label: 'Male' },
  { value: 'F', label: 'Female' },
  { value: 'O', label: 'Other' }
]

async function loadMe() {
  try {
    const me = await json('/api/users/me/')
    profile.value = {
      username: me.username || '',
      email: me.email || '',
      full_name: me.full_name || '',
      avatar: me.avatar || '',
      gender: me.gender || '',
      phone: me.phone || '',
      address: me.address || '',
      about: me.about || '',
      birth_date: me.birth_date || '',
      website: me.website || '',
      location: me.location || '',
    }
  } catch (e) {
    showMessage('Could not load profile', 'error')
  }
}

async function saveProfile() {
  if (!profile.value.username || !profile.value.email || !profile.value.full_name) {
    showMessage('Username, email and full name are required', 'error')
    return
  }

  savingProfile.value = true
  try {
    await json('/api/users/me/', { method: 'PATCH', body: JSON.stringify(profile.value) })
    await session.fetchMe().catch(() => {})
    showMessage('Profile updated successfully!', 'success')
  } catch (e) {
    showMessage('Update failed. Please try again.', 'error')
  } finally {
    savingProfile.value = false
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
  loadMe()
})
</script>

<template>
  <div class="container">
    <div style="display:flex; align-items:center; gap:8px; margin:0 0 24px;">
      <h2 style="margin:0; font-size:22px; font-weight:700;">Edit Profile</h2>
      <div v-if="message" style="margin-left:auto; padding:8px 16px; border-radius:8px; font-size:13px; font-weight:500;" :style="messageType === 'success' ? 'background:#dcfce7; color:#166534; border:1px solid #bbf7d0;' : 'background:#fee2e2; color:#b91c1c; border:1px solid #fecaca;'">
        {{ message }}
      </div>
    </div>

    <div class="card" style="padding:24px; max-width:800px;">
      <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">
        <div style="width:48px; height:48px; background:linear-gradient(135deg,#ff4db0,#4db2ff); border-radius:12px; display:grid; place-items:center; color:#fff; font-weight:600; font-size:20px;">
          👤
        </div>
        <div>
          <h3 style="margin:0; font-size:18px; font-weight:600;">Profile Information</h3>
          <p style="margin:4px 0 0; color:var(--c-text-muted); font-size:14px;">Update your personal information and profile details</p>
        </div>
      </div>

      <form @submit.prevent="saveProfile" style="display:grid; gap:20px;">
        <!-- Basic Information -->
        <div style="display:grid; gap:16px;">
          <h4 style="margin:0; font-size:16px; font-weight:600; color:var(--c-text);">Basic Information</h4>

          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
            <label style="display:grid; gap:6px;">
              <span style="font-size:13px; color:var(--c-text-muted); font-weight:500;">Username *</span>
              <input v-model="profile.username" type="text" required style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px;" />
            </label>
            <label style="display:grid; gap:6px;">
              <span style="font-size:13px; color:var(--c-text-muted); font-weight:500;">Full Name *</span>
              <input v-model="profile.full_name" type="text" required style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px;" />
            </label>
          </div>

          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
            <label style="display:grid; gap:6px;">
              <span style="font-size:13px; color:var(--c-text-muted); font-weight:500;">Email *</span>
              <input v-model="profile.email" type="email" required style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px;" />
            </label>
            <label style="display:grid; gap:6px;">
              <span style="font-size:13px; color:var(--c-text-muted); font-weight:500;">Phone</span>
              <input v-model="profile.phone" type="tel" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px;" />
            </label>
          </div>

          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
            <label style="display:grid; gap:6px;">
              <span style="font-size:13px; color:var(--c-text-muted); font-weight:500;">Gender</span>
              <select v-model="profile.gender" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px;">
                <option v-for="option in genderOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </label>
            <label style="display:grid; gap:6px;">
              <span style="font-size:13px; color:var(--c-text-muted); font-weight:500;">Birth Date</span>
              <input v-model="profile.birth_date" type="date" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px;" />
            </label>
          </div>
        </div>

        <!-- Profile Details -->
        <div style="display:grid; gap:16px;">
          <h4 style="margin:0; font-size:16px; font-weight:600; color:var(--c-text);">Profile Details</h4>

          <label style="display:grid; gap:6px;">
            <span style="font-size:13px; color:var(--c-text-muted); font-weight:500;">Avatar URL</span>
            <input v-model="profile.avatar" type="url" placeholder="https://example.com/avatar.jpg" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px;" />
            <div style="font-size:12px; color:var(--c-text-muted);">Enter a URL to your profile picture</div>
          </label>

          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
            <label style="display:grid; gap:6px;">
              <span style="font-size:13px; color:var(--c-text-muted); font-weight:500;">Website</span>
              <input v-model="profile.website" type="url" placeholder="https://example.com" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px;" />
            </label>
            <label style="display:grid; gap:6px;">
              <span style="font-size:13px; color:var(--c-text-muted); font-weight:500;">Location</span>
              <input v-model="profile.location" type="text" placeholder="City, Country" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px;" />
            </label>
          </div>

          <label style="display:grid; gap:6px;">
            <span style="font-size:13px; color:var(--c-text-muted); font-weight:500;">Address</span>
            <textarea v-model="profile.address" rows="2" placeholder="Enter your address" style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px; resize:vertical;"></textarea>
          </label>

          <label style="display:grid; gap:6px;">
            <span style="font-size:13px; color:var(--c-text-muted); font-weight:500;">About</span>
            <textarea v-model="profile.about" rows="4" placeholder="Tell us about yourself, your interests, hobbies, or anything you'd like to share..." style="border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:10px 12px; font-size:14px; resize:vertical;"></textarea>
            <div style="font-size:12px; color:var(--c-text-muted);">Share a bit about yourself with other users</div>
          </label>
        </div>

        <div style="display:flex; justify-content:flex-end; padding-top:16px; border-top:1px solid var(--c-border);">
          <button :disabled="savingProfile" style="border:1px solid var(--c-accent); background:var(--c-accent); color:white; border-radius:10px; padding:12px 24px; cursor:pointer; font-size:14px; font-weight:500;">
            {{ savingProfile ? 'Saving…' : 'Save Profile' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

input, select, textarea {
  transition: all 0.2s ease;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: var(--c-accent);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

button:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
