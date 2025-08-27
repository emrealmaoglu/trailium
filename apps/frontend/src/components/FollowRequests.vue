<template>
  <div class="follow-requests">
    <h3 class="section-title">Follow Requests</h3>

    <div v-if="loading" class="loading">
      Loading follow requests...
    </div>

    <div v-else-if="followRequests.length === 0" class="no-requests">
      No pending follow requests
    </div>

    <div v-else class="requests-list">
      <div
        v-for="request in followRequests"
        :key="request.id"
        class="request-item"
      >
        <div class="user-info">
          <div class="avatar">
            <img
              v-if="request.follower.avatar"
              :src="request.follower.avatar"
              :alt="request.follower.username"
            />
            <span v-else class="avatar-placeholder">
              {{ request.follower.username.charAt(0).toUpperCase() }}
            </span>
          </div>
          <div class="user-details">
            <div class="username">{{ request.follower.username }}</div>
            <div class="full-name" v-if="request.follower.full_name">
              {{ request.follower.full_name }}
            </div>
          </div>
        </div>

        <div class="actions">
          <button
            @click="approveRequest(request.id)"
            :disabled="processing === request.id"
            class="btn-approve"
          >
            {{ processing === request.id ? 'Approving...' : 'Approve' }}
          </button>
          <button
            @click="rejectRequest(request.id)"
            :disabled="processing === request.id"
            class="btn-reject"
          >
            {{ processing === request.id ? 'Rejecting...' : 'Reject' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { json } from '@/lib/http'

const followRequests = ref([])
const loading = ref(true)
const processing = ref(null)

async function fetchFollowRequests() {
  try {
    loading.value = true
    const response = await json('/api/follows/pending/')
    followRequests.value = response
  } catch (error) {
    console.error('Failed to fetch follow requests:', error)
  } finally {
    loading.value = false
  }
}

async function approveRequest(requestId) {
  try {
    processing.value = requestId
    await json(`/api/follows/${requestId}/approve/`, { method: 'POST' })
    // Remove the approved request from the list
    followRequests.value = followRequests.value.filter(req => req.id !== requestId)
  } catch (error) {
    console.error('Failed to approve follow request:', error)
  } finally {
    processing.value = null
  }
}

async function rejectRequest(requestId) {
  try {
    processing.value = requestId
    await json(`/api/follows/${requestId}/reject/`, { method: 'POST' })
    // Remove the rejected request from the list
    followRequests.value = followRequests.value.filter(req => req.id !== requestId)
  } catch (error) {
    console.error('Failed to reject follow request:', error)
  } finally {
    processing.value = null
  }
}

onMounted(() => {
  fetchFollowRequests()
})
</script>

<style scoped>
.follow-requests {
  padding: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--c-text);
}

.loading, .no-requests {
  text-align: center;
  padding: 40px;
  color: var(--c-text-muted);
}

.requests-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.request-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border: 1px solid var(--c-border);
  border-radius: 12px;
  background: var(--c-surface);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--c-surface-2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 20px;
  font-weight: 600;
  color: var(--c-text-muted);
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.username {
  font-weight: 600;
  color: var(--c-text);
}

.full-name {
  font-size: 14px;
  color: var(--c-text-muted);
}

.actions {
  display: flex;
  gap: 8px;
}

.btn-approve, .btn-reject {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-approve {
  background: #10b981;
  color: white;
}

.btn-approve:hover:not(:disabled) {
  background: #059669;
}

.btn-reject {
  background: #ef4444;
  color: white;
}

.btn-reject:hover:not(:disabled) {
  background: #dc2626;
}

.btn-approve:disabled, .btn-reject:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
