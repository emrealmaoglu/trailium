<script setup>
/**
 * Kullanıcılar sayfası (stub): i18n ile metinler.
 */
import { ref, onMounted, onUnmounted, computed, inject, watch } from 'vue'
import { json, clearCache } from '@/lib/http'
import { useSessionStore } from '@/stores/session'
import UserCard from '@/components/UserCard.vue'
import UserCardSkeleton from '@/components/UserCardSkeleton.vue'
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import { useI18n } from 'vue-i18n'

const session = useSessionStore()

// State management
const loading = ref(true)
const users = ref([])
const errorMsg = ref('')
const page = ref(1)
const nextUrl = ref('')
const prevUrl = ref('')
const total = ref(0)

// Search and filters
const searchQuery = ref('')
const searchTimeout = ref(null)
const showFilters = ref(false)
const filterPremium = ref(false)
const filterPrivate = ref(false)

// Computed properties
const filteredUsers = computed(() => {
  let filtered = users.value

  if (filterPremium.value) {
    filtered = filtered.filter(u => u.is_premium)
  }

  if (filterPrivate.value) {
    filtered = filtered.filter(u => u.is_private)
  }

  return filtered
})

const hasActiveFilters = computed(() =>
  filterPremium.value || filterPrivate.value || searchQuery.value.trim()
)

const { t } = useI18n()
const title = computed(() => t('users.title'))

// Notifications
const showNotification = inject('showNotification')

// User mapping function
function mapUser(user) {
  return {
    id: user.id,
    name: user.full_name || user.username,
    email: user.email,
    phone: user.phone || 'No phone',
    addressText: user.address || '',
    companyName: user.company_name || '',
    website: user.website || '',
    is_premium: user.is_premium || false,
    is_private: user.is_private || false,
    avatar: user.avatar || '',
    about: user.about || '',
    created_at: user.date_joined || user.created_at
  }
}

// Utility functions
function getPageFromUrl(url) {
  try {
    const urlObj = new URL(url)
    const pageParam = urlObj.searchParams.get('page')
    return pageParam ? parseInt(pageParam, 10) : null
  } catch {
    return null
  }
}

function validateSearchQuery(query) {
  return query.trim().length >= 2
}

// API functions
async function fetchData(input = `/api/users/?page=${page.value}`) {
  loading.value = true
  errorMsg.value = ''

  try {
    const payload = await json(input)
    const data = Array.isArray(payload) ? payload : payload.results || []

    // Filter out current user and admin users
    const currentUser = session.user?.username
    const filteredData = data.filter(user =>
      user.username !== currentUser &&
      !user.is_superuser &&
      !user.is_staff
    )

    users.value = filteredData.map(mapUser)

    if (!Array.isArray(payload)) {
      nextUrl.value = payload.next || ''
      prevUrl.value = payload.previous || ''
      total.value = payload.count || 0

      const inferredPage = getPageFromUrl(input)
      if (inferredPage) page.value = inferredPage
    }

    if (users.value.length === 0) {
      errorMsg.value = 'No other users available yet.'
    }

  } catch (error) {
    console.error('Failed to fetch users:', error)
    errorMsg.value = 'Could not load users. Please retry.'
    showNotification('Failed to load users', 'error', 5000)
  } finally {
    loading.value = false
  }
}

async function searchUsers() {
  const query = searchQuery.value.trim()

  if (!validateSearchQuery(query)) {
    return
  }

  try {
    loading.value = true
    const payload = await json(`/api/users/?search=${encodeURIComponent(query)}`)
    const data = Array.isArray(payload) ? payload : payload.results || []

    // Filter out admin users from search results
    const filteredData = data.filter(user =>
      !user.is_superuser &&
      !user.is_staff
    )

    users.value = filteredData.map(mapUser)
    nextUrl.value = payload.next || ''
    prevUrl.value = payload.previous || ''
    total.value = payload.count || 0
    page.value = 1

  } catch (error) {
    console.error('Search failed:', error)
    errorMsg.value = 'Search failed. Please try again.'
    showNotification('Search failed', 'error', 5000)
  } finally {
    loading.value = false
  }
}

// Event handlers
function handleSearchInput() {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }

  searchTimeout.value = setTimeout(() => {
    if (searchQuery.value.trim()) {
      searchUsers()
    } else {
      fetchData()
    }
  }, 300) // Reduced from 500ms for better UX
}

function nextPage() {
  if (nextUrl.value && !loading.value) {
    fetchData(nextUrl.value)
  }
}

function prevPage() {
  if (prevUrl.value && !loading.value) {
    fetchData(prevUrl.value)
  }
}

function clearFilters() {
  filterPremium.value = false
  filterPrivate.value = false
  searchQuery.value = ''

  // Clear cache for users endpoint
  clearCache('/api/users/')

  fetchData()
}

// Lifecycle
onMounted(() => {
  fetchData()

  // Refresh data when tab becomes visible
  const onVisibilityChange = () => {
    if (document.visibilityState === 'visible') {
      fetchData(`/api/users/?page=${page.value}`)
    }
  }

  document.addEventListener('visibilitychange', onVisibilityChange)

  onUnmounted(() => {
    document.removeEventListener('visibilitychange', onVisibilityChange)
  })
})

// Watch for filter changes to update cache
watch([filterPremium, filterPrivate], () => {
  // Clear cache when filters change
  clearCache('/api/users/')
})
</script>

<template>
  <div class="users-page">
    <Breadcrumbs />

    <!-- Header Section -->
    <div class="users-header">
      <h2 class="users-title">{{ title }}</h2>

      <div class="users-controls">
        <button
          @click="showFilters = !showFilters"
          class="filter-toggle-btn"
          :class="{ 'active': showFilters }"
        >
          🔍 {{ t('users.filters') }}
        </button>

        <div class="search-container">
          <input
            v-model="searchQuery"
            @input="handleSearchInput"
            :placeholder="t('users.searchPlaceholder')"
            class="search-input"
            type="search"
          />
          <span class="search-icon">🔍</span>
        </div>
      </div>
    </div>

    <!-- Filters Panel -->
    <div v-if="showFilters" class="filters-panel">
      <div class="filters-content">
        <label class="filter-checkbox">
          <input
            type="checkbox"
            v-model="filterPremium"
            class="filter-input"
          />
          <span class="filter-label">{{ t('users.premiumOnly') }}</span>
        </label>

        <label class="filter-checkbox">
          <input
            type="checkbox"
            v-model="filterPrivate"
            class="filter-input"
          />
          <span class="filter-label">{{ t('users.privateOnly') }}</span>
        </label>

        <button @click="clearFilters" class="clear-filters-btn">
          {{ t('users.clearFilters') }}
        </button>
      </div>
    </div>

    <!-- Content Section -->
    <div class="users-content">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>{{ t('users.loading') }}</p>
      </div>

      <!-- Error State -->
      <div v-else-if="errorMsg" class="error-state">
        <div class="error-icon">❌</div>
        <p>{{ errorMsg }}</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredUsers.length === 0" class="empty-state">
        <div class="empty-icon">👥</div>
        <h3>No users found</h3>
        <p>
          {{ hasActiveFilters ? t('users.searchPlaceholder') : t('users.emptyHint') }}
        </p>
      </div>

      <!-- Users Grid -->
      <div v-else class="users-grid" data-testid="users-grid">
        <UserCard
          v-for="user in filteredUsers"
          :key="user.id"
          :user="user"
        />
      </div>
    </div>

    <!-- Pagination Section -->
    <div class="pagination-section">
      <div class="pagination-info">
        <span class="user-count">
          {{ t('users.showing') }} {{ filteredUsers.length }} {{ t('users.of') }} {{ total }} {{ t('users.usersWord') }}
        </span>
        <span v-if="hasActiveFilters" class="filtered-indicator">
          (filtered)
        </span>
      </div>

      <div class="pagination-controls">
        <button
          :disabled="!prevUrl || loading"
          @click="prevPage"
          class="pagination-btn"
          :class="{ 'disabled': !prevUrl || loading }"
        >
          ← Previous
        </button>

        <span class="page-info">Page {{ page }}</span>

        <button
          :disabled="!nextUrl || loading"
          @click="nextPage"
          class="pagination-btn"
          :class="{ 'disabled': !nextUrl || loading }"
        >
          Next →
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.users-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

.users-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.users-title {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--c-text);
}

.users-controls {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-toggle-btn {
  padding: 10px 16px;
  border: 2px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-text);
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 100px;
}

.filter-toggle-btn:hover {
  background: var(--c-surface-2);
  border-color: var(--c-accent);
  transform: translateY(-1px);
}

.filter-toggle-btn.active {
  background: var(--c-accent);
  color: white;
  border-color: var(--c-accent);
}

.search-container {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  border: 2px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-text);
  border-radius: 12px;
  padding: 10px 16px 10px 44px;
  font-size: 14px;
  width: 240px;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--c-accent);
  box-shadow: 0 0 0 3px rgba(95, 55, 210, 0.1);
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--c-text-muted);
  font-size: 16px;
}

.filters-panel {
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
}

.filters-content {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.filter-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.filter-input {
  width: 18px;
  height: 18px;
  accent-color: var(--c-accent);
}

.filter-label {
  font-size: 14px;
  color: var(--c-text);
  font-weight: 500;
}

.clear-filters-btn {
  padding: 8px 16px;
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-text);
  border-radius: 10px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-filters-btn:hover {
  background: var(--c-surface-2);
  border-color: var(--c-accent);
}

.users-content {
  min-height: 400px;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: var(--c-text-muted);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--c-border);
  border-top: 4px solid var(--c-accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon,
.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--c-text);
}

.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-top: 1px solid var(--c-border);
  flex-wrap: wrap;
  gap: 16px;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-count {
  color: var(--c-text-muted);
  font-size: 14px;
}

.filtered-indicator {
  color: var(--c-accent);
  font-size: 14px;
  font-weight: 500;
}

.pagination-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.pagination-btn {
  padding: 8px 16px;
  border: 2px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-text);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 80px;
}

.pagination-btn:hover:not(.disabled) {
  background: var(--c-accent);
  color: white;
  border-color: var(--c-accent);
  transform: translateY(-1px);
}

.pagination-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: var(--c-text-muted);
  font-weight: 500;
  min-width: 60px;
  text-align: center;
}

/* Responsive Design */
@media (max-width: 768px) {
  .users-header {
    flex-direction: column;
    align-items: stretch;
  }

  .users-controls {
    justify-content: stretch;
  }

  .search-input {
    width: 100%;
    min-width: 200px;
  }

  .filters-content {
    flex-direction: column;
    align-items: stretch;
  }

  .pagination-section {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }

  .users-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .users-page {
    padding: 0 12px;
  }

  .users-title {
    font-size: 24px;
  }

  .filter-toggle-btn,
  .search-input {
    font-size: 16px; /* Prevent zoom on iOS */
  }
}
</style>
