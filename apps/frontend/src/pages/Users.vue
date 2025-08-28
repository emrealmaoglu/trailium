<script setup>
/**
 * Kullanıcılar sayfası: liste + sayfalama + durumlar.
 */
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUsersStore } from '@/stores/users'
import UserCard from '@/components/UserCard.vue'
import Pagination from '@/components/Pagination.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const title = computed(() => t('users.title'))
const usersStore = useUsersStore()
const route = useRoute()
const router = useRouter()

const localPage = ref(Number(route.query.page ?? 1) || 1)

onMounted(async () => {
  await usersStore.fetchUsers({ page: localPage.value })
})

function onChangePage(p) {
  usersStore.fetchUsers({ page: p })
  router.push({ path: '/users', query: { page: String(p) } })
}
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
      <div v-if="usersStore.loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>{{ t('users.loading') }}</p>
      </div>

      <!-- Error State -->
      <div v-else-if="usersStore.error" class="error-state">
        <div class="error-icon">❌</div>
        <p>{{ t('users.error') }}</p>
        <button class="filter-toggle-btn" @click="() => usersStore.fetchUsers({ page: localPage })">{{ t('users.retry') }}</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="usersStore.users.length === 0" class="empty-state">
        <div class="empty-icon">👥</div>
        <h3>{{ t('users.emptyTitle') }}</h3>
        <p>{{ t('users.empty') }}</p>
      </div>

      <!-- Users Grid -->
      <div v-else class="users-grid" data-testid="users-grid">
        <UserCard
          v-for="user in usersStore.users"
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

      <Pagination
        :page="usersStore.page"
        :total-pages="usersStore.totalPages"
        :disabled="usersStore.loading"
        @update:page="onChangePage"
      />
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
