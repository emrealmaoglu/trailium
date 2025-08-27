<script setup>
import IconPin from './icons/IconPin.vue'
import IconBuilding from './icons/IconBuilding.vue'
import IconGlobe from './icons/IconGlobe.vue'
import { useRouter } from 'vue-router'
import { ref, onMounted, computed } from 'vue'
import { json } from '@/lib/http'

const props = defineProps({
  user: {
    type: Object,
    required: true,
    // expected shape: { id, name, email, phone, addressText, companyName, website, is_premium, is_private, avatar, about, created_at }
  }
})

const router = useRouter()
const goToDetail = () => {
  if (props.user && props.user.id != null) {
    router.push(`/users/${props.user.id}/todos`)
  }
}

// Computed properties
const userInitials = computed(() => {
  const name = props.user?.name || ''
  return name.trim().charAt(0).toUpperCase()
})

const displayName = computed(() => {
  return props.user?.name || 'Unknown User'
})

const displayEmail = computed(() => {
  return props.user?.email || 'No email'
})

const displayPhone = computed(() => {
  return props.user?.phone || 'No phone'
})

const hasContactInfo = computed(() => {
  return props.user?.addressText || props.user?.companyName || props.user?.website
})

const isNewUser = computed(() => {
  if (!props.user?.created_at) return false
  const createdDate = new Date(props.user.created_at)
  const now = new Date()
  const daysDiff = (now - createdDate) / (1000 * 60 * 60 * 24)
  return daysDiff <= 7 // New if created within 7 days
})

// Follow functionality
const followStatus = ref('unknown') // unknown|following|pending|none
const followBusy = ref(false)

async function toggleFollow(e) {
  e.stopPropagation()
  if (!props.user?.id || followBusy.value) return

  followBusy.value = true
  try {
    if (followStatus.value === 'following' || followStatus.value === 'pending') {
      await json(`/api/follows/users/${props.user.id}/unfollow/`, { method: 'POST' })
      followStatus.value = 'none'
    } else {
      const response = await json(`/api/follows/users/${props.user.id}/follow/`, { method: 'POST' })
      // Check if user is private and show appropriate message
      if (props.user.is_private) {
        followStatus.value = 'pending'
        // Show notification that request was sent
        if (window.showNotification) {
          window.showNotification('Follow request sent! Waiting for approval.', 'info', 3000)
        }
      } else {
        followStatus.value = 'following'
      }
    }
  } catch (error) {
    console.error('Follow action failed:', error)
  } finally {
    followBusy.value = false
  }
}

// Check current follow status on mount
onMounted(async () => {
  if (!props.user?.id) return
  try {
    const response = await json(`/api/follows/users/${props.user.id}/status/`)
    followStatus.value = response.status || 'none'
  } catch (error) {
    console.error('Failed to fetch follow status:', error)
    followStatus.value = 'none'
  }
})
</script>

<template>
  <article
    class="user-card"
    tabindex="0"
    role="button"
    @click="goToDetail"
    @keydown.enter="goToDetail"
    @keydown.space="goToDetail"
  >
    <!-- User Header -->
    <header class="user-header">
      <div class="user-avatar">
        <img
          v-if="user.avatar"
          :src="user.avatar"
          :alt="displayName"
          class="avatar-image"
        />
        <div v-else class="avatar-placeholder">
          {{ userInitials }}
        </div>

        <!-- Premium badge -->
        <div v-if="user.is_premium" class="premium-badge" title="Premium User">
          ⭐
        </div>

        <!-- New user indicator -->
        <div v-if="isNewUser" class="new-user-badge" title="New User">
          🆕
        </div>
      </div>

      <div class="user-info">
        <div class="user-name-section">
          <h3 class="user-name">{{ displayName }}</h3>

          <!-- Private account indicator -->
          <span v-if="user.is_private" class="private-indicator" title="Private Account">
            🔒
          </span>
        </div>

        <div class="user-contact">
          <span class="user-email">{{ displayEmail }}</span>
          <span class="contact-separator">·</span>
          <span class="user-phone">{{ displayPhone }}</span>
        </div>
      </div>

      <!-- Follow Button -->
      <button
        @click="toggleFollow"
        :disabled="followBusy"
        class="follow-btn"
        :class="{ 'busy': followBusy }"
        title="Follow this user"
      >
        <span v-if="followBusy" class="loading-dots">...</span>
        <span v-else-if="followStatus === 'following'" class="following-text">
          Takip Ediliyor
        </span>
        <span v-else-if="followStatus === 'pending'" class="pending-text">
          Takip İsteği Gönderildi
        </span>
        <span v-else-if="user.is_private" class="follow-request-text">
          Takip İsteği Gönder
        </span>
        <span v-else class="follow-text">
          Takip Et
        </span>
      </button>
    </header>

    <!-- Divider -->
    <div class="card-divider"></div>

    <!-- User Details -->
    <div v-if="hasContactInfo" class="user-details">
      <div v-if="user.addressText" class="detail-item">
        <IconPin class="detail-icon" />
        <span class="detail-text">{{ user.addressText }}</span>
      </div>

      <div v-if="user.companyName" class="detail-item">
        <IconBuilding class="detail-icon" />
        <span class="detail-text">{{ user.companyName }}</span>
      </div>

      <div v-if="user.website" class="detail-item">
        <IconGlobe class="detail-icon" />
        <span class="detail-text">{{ user.website }}</span>
      </div>
    </div>

    <!-- About Section -->
    <div v-if="user.about" class="user-about">
      <p class="about-text">{{ user.about }}</p>
    </div>

    <!-- User Stats -->
    <div class="user-stats">
      <div class="stat-item">
        <span class="stat-label">Member since</span>
        <span class="stat-value">
          {{ user.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown' }}
        </span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.user-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.user-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: var(--c-accent);
}

.user-card:focus {
  outline: 2px solid var(--c-accent);
  outline-offset: 2px;
}

/* User Header */
.user-header {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 16px;
}

.user-avatar {
  position: relative;
  flex-shrink: 0;
}

.avatar-image {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff4db0, #4db2ff);
  display: grid;
  place-items: center;
  color: var(--c-text);
  font-weight: 600;
  font-size: 20px;
  position: relative;
}

.premium-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #ffd700, #ffb347);
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 12px;
  color: #000;
  font-weight: bold;
  border: 2px solid var(--c-bg);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.new-user-badge {
  position: absolute;
  bottom: -6px;
  left: -6px;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #4ade80, #22c55e);
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 12px;
  color: var(--c-text);
  font-weight: bold;
  border: 2px solid var(--c-bg);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name-section {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.user-name {
  font-weight: 600;
  font-size: 18px;
  color: var(--c-text);
  margin: 0;
  line-height: 1.2;
}

.private-indicator {
  font-size: 14px;
  color: var(--c-text-muted);
  opacity: 0.8;
}

.user-contact {
  color: var(--c-text-muted);
  font-size: 14px;
  line-height: 1.4;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.contact-separator {
  opacity: 0.5;
}

.user-email,
.user-phone {
  word-break: break-word;
}

/* Follow Button */
.follow-btn {
  margin-left: auto;
  border: 2px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-text);
  border-radius: 12px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
  min-width: 120px;
  white-space: nowrap;
  flex-shrink: 0;
}

.follow-btn:hover:not(:disabled) {
  background: var(--c-accent);
  color: white;
  border-color: var(--c-accent);
  transform: translateY(-1px);
}

.follow-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.follow-btn.busy {
  background: var(--c-surface-2);
  color: var(--c-text-muted);
}

.loading-dots {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Card Divider */
.card-divider {
  height: 1px;
  background: var(--c-border);
  margin: 16px 0;
  opacity: 0.6;
}

/* User Details */
.user-details {
  display: grid;
  gap: 12px;
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 14px;
  color: var(--c-text-muted);
}

.detail-icon {
  width: 16px;
  height: 16px;
  opacity: 0.7;
  flex-shrink: 0;
}

.detail-text {
  word-break: break-word;
  line-height: 1.4;
}

/* User About */
.user-about {
  margin-bottom: 16px;
  padding: 12px;
  background: var(--c-surface-2);
  border-radius: 8px;
  border: 1px solid var(--c-border);
}

.about-text {
  margin: 0;
  font-size: 14px;
  color: var(--c-text);
  line-height: 1.5;
  word-break: break-word;
}

/* User Stats */
.user-stats {
  display: flex;
  gap: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--c-border);
  opacity: 0.8;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 11px;
  color: var(--c-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 13px;
  color: var(--c-text);
  font-weight: 500;
}

/* Responsive Design */
@media (max-width: 768px) {
  .user-card {
    padding: 16px;
  }

  .user-header {
    gap: 12px;
  }

  .avatar-placeholder {
    width: 48px;
    height: 48px;
    font-size: 18px;
  }

  .user-name {
    font-size: 16px;
  }

  .follow-btn {
    min-width: 100px;
    padding: 6px 12px;
    font-size: 12px;
  }

  .user-contact {
    flex-direction: column;
    gap: 4px;
    align-items: flex-start;
  }

  .contact-separator {
    display: none;
  }
}

@media (max-width: 480px) {
  .user-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .follow-btn {
    align-self: stretch;
    margin-left: 0;
  }

  .user-stats {
    flex-direction: column;
    gap: 8px;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .user-card {
    border-width: 2px;
  }

  .card-divider {
    height: 2px;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .user-card,
  .follow-btn {
    transition: none;
  }

  .user-card:hover {
    transform: none;
  }
}
</style>
