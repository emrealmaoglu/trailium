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

const uploadingPhoto = ref(false)
const selectedPhoto = ref(null)

const genderOptions = [
  { value: '', label: 'Prefer not to say' },
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
  { value: 'prefer_not_to_say', label: 'Prefer not to say' },
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
    // Only send fields accepted by backend serializer
    const payload = {
      username: profile.value.username,
      email: profile.value.email,
      full_name: profile.value.full_name,
      avatar: profile.value.avatar,
      gender: profile.value.gender,
      phone: profile.value.phone,
      address: profile.value.address,
      about: profile.value.about,
      // is_private is supported by backend; include if present in UI later
    }
    await json('/api/users/me/', { method: 'PATCH', body: JSON.stringify(payload) })
    await session.fetchMe().catch(() => {})
    showMessage('Profile updated successfully!', 'success')
  } catch (e) {
    const msg = (e && e.message) ? e.message : 'Update failed. Please try again.'
    showMessage(msg, 'error')
  } finally {
    savingProfile.value = false
  }
}

async function handlePhotoUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  // Validate file size (5MB max)
  if (file.size > 5 * 1024 * 1024) {
    showMessage('File size must be less than 5MB', 'error')
    return
  }

  // Validate file type
  if (!file.type.startsWith('image/')) {
    showMessage('Please select an image file', 'error')
    return
  }

  selectedPhoto.value = file
  uploadingPhoto.value = true

  try {
    const formData = new FormData()
    formData.append('avatar', file)

    const response = await json('/api/users/me/', {
      method: 'PATCH',
      body: formData,
      headers: {} // Let browser set content-type for FormData
    })

    // Update profile avatar
    profile.value.avatar = response.avatar

    // Update session user avatar
    if (session.user) {
      session.user.avatar = response.avatar
    }

    showMessage('Profile photo updated successfully!', 'success')

    // Clear file input
    event.target.value = ''
    selectedPhoto.value = null
  } catch (error) {
    showMessage('Failed to upload profile photo. Please try again.', 'error')
  } finally {
    uploadingPhoto.value = false
  }
}

async function removeProfilePhoto() {
  if (!confirm('Are you sure you want to remove your profile photo?')) return

  try {
    const response = await json('/api/users/me/', {
      method: 'PATCH',
      body: JSON.stringify({ avatar: '' })
    })

    // Update profile avatar
    profile.value.avatar = ''

    // Update session user avatar
    if (session.user) {
      session.user.avatar = ''
    }

    showMessage('Profile photo removed successfully!', 'success')
  } catch (error) {
    showMessage('Failed to remove profile photo. Please try again.', 'error')
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
    <div class="page-header">
      <h2 class="page-title">Edit Profile</h2>
      <div v-if="message" class="message" :class="messageType">
        {{ message }}
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <div class="card-icon">
          👤
        </div>
        <div>
          <h3 class="card-title">Profile Information</h3>
          <p class="card-subtitle">Update your personal information and profile details</p>
        </div>
      </div>

      <form @submit.prevent="saveProfile" class="profile-form">
        <!-- Basic Information -->
        <div class="form-section">
          <h4 class="section-title">Basic Information</h4>

          <div class="form-row">
            <label class="form-label">
              <span class="label-text">Username *</span>
              <input v-model="profile.username" type="text" required class="form-input" />
            </label>
            <label class="form-label">
              <span class="label-text">Full Name *</span>
              <input v-model="profile.full_name" type="text" required class="form-input" />
            </label>
          </div>

          <div class="form-row">
            <label class="form-label">
              <span class="label-text">Email *</span>
              <input v-model="profile.email" type="email" required class="form-input" />
            </label>
            <label class="form-label">
              <span class="label-text">Phone</span>
              <input v-model="profile.phone" type="tel" class="form-input" />
            </label>
          </div>

          <div class="form-row">
            <label class="form-label">
              <span class="label-text">Gender</span>
              <select v-model="profile.gender" class="form-select">
                <option v-for="option in genderOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </label>
            <label class="form-label">
              <span class="label-text">Birth Date</span>
              <input v-model="profile.birth_date" type="date" class="form-input" />
            </label>
          </div>
        </div>

        <!-- Profile Photo -->
        <div class="form-section">
          <h4 class="section-title">Profile Photo</h4>
          <p class="section-description">Upload and manage your profile picture here. This photo will be visible to other users.</p>

          <!-- Current Avatar Display -->
          <div class="avatar-section">
            <div class="avatar-container">
              <img
                v-if="profile.avatar"
                :src="profile.avatar"
                alt="Profile Photo"
                class="avatar-image"
              />
              <div v-else class="avatar-placeholder">
                {{ profile.full_name ? profile.full_name.charAt(0).toUpperCase() : 'U' }}
              </div>
            </div>

            <div class="upload-section">
              <label class="form-label">
                <span class="label-text">Upload New Photo</span>
                <input
                  type="file"
                  accept="image/*"
                  @change="handlePhotoUpload"
                  class="file-input"
                />
                <div class="help-text">Choose a JPG, PNG or GIF file (max 5MB)</div>
              </label>

              <button
                v-if="profile.avatar"
                type="button"
                @click="removeProfilePhoto"
                class="btn-remove-photo"
              >
                Remove Photo
              </button>
            </div>
          </div>
        </div>

        <!-- Profile Details -->
        <div class="form-section">
          <h4 class="section-title">Profile Details</h4>

          <div class="form-row">
            <label class="form-label">
              <span class="label-text">Website</span>
              <input v-model="profile.website" type="url" placeholder="https://example.com" class="form-input" />
            </label>
            <label class="form-label">
              <span class="label-text">Location</span>
              <input v-model="profile.location" type="text" placeholder="City, Country" class="form-input" />
            </label>
          </div>

          <label class="form-label">
            <span class="label-text">Address</span>
            <textarea v-model="profile.address" rows="2" placeholder="Enter your address" class="form-textarea"></textarea>
          </label>

          <label class="form-label">
            <span class="label-text">About</span>
            <textarea v-model="profile.about" rows="4" placeholder="Tell us about yourself, your interests, hobbies, or anything you'd like to share..." class="form-textarea"></textarea>
            <div class="help-text">Share a bit about yourself with other users</div>
          </label>
        </div>

        <div class="form-actions">
          <button :disabled="savingProfile" class="btn-save">
            {{ savingProfile ? 'Saving…' : 'Save Profile' }}
          </button>
        </div>
      </form>
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

.card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
  max-width: 800px;
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
  background: linear-gradient(135deg, #ff4db0, #4db2ff);
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 600;
  font-size: 20px;
}

.card-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.card-subtitle {
  margin: 4px 0 0;
  color: var(--c-text-muted);
  font-size: 14px;
}

/* Form Layout */
.profile-form {
  display: grid;
  gap: 20px;
}

.form-section {
  display: grid;
  gap: 16px;
}

.section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--c-text);
}

.section-description {
  margin: 0 0 16px;
  font-size: 14px;
  color: var(--c-text-muted);
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

.help-text {
  font-size: 12px;
  color: var(--c-text-muted);
}

/* Form Inputs */
.form-input,
.form-select,
.form-textarea {
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-text);
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 14px;
  transition: all 0.2s ease;
  resize: vertical;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--c-accent);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* Avatar Section */
.avatar-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-container {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid var(--c-border);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: var(--c-surface-2);
  display: grid;
  place-items: center;
  color: var(--c-text-muted);
  font-size: 24px;
  font-weight: 600;
}

.upload-section {
  display: grid;
  gap: 8px;
}

.file-input {
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-text);
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 14px;
  cursor: pointer;
}

.btn-remove-photo {
  border: 1px solid #fecaca;
  background: #fee2e2;
  color: #b91c1c;
  border-radius: 8px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  align-self: flex-start;
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid var(--c-border);
}

.btn-save {
  border: 1px solid var(--c-accent);
  background: var(--c-accent);
  color: white;
  border-radius: 10px;
  padding: 12px 24px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-save:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive Design */
@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .avatar-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .card {
    padding: 16px;
  }
}
</style>
