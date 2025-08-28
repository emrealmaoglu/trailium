<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ref, inject, computed, onMounted, onUnmounted } from 'vue'
import { useSessionStore } from '@/stores/session'
import { json } from '@/lib/http'
import logoSrc from '../assets/brand/N2Mobil-Logotype.png'
import UserMenu from '@/components/UserMenu.vue'

const sessionStore = useSessionStore()
const showNotification = inject('showNotification')

// Responsive state
const isMobile = ref(false)
const sidebarOpen = ref(false)
const isTablet = ref(false)
const pendingRequests = ref(0)

// Computed
const isAdmin = computed(() => sessionStore.user?.is_superuser)

// Responsive detection
function checkScreenSize() {
  const width = window.innerWidth
  isMobile.value = width < 768
  isTablet.value = width >= 768 && width < 1024

  // Auto-close sidebar on mobile when screen size changes
  if (width >= 768) {
    sidebarOpen.value = false
  }
}

// Toggle sidebar
function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value
}

// Close sidebar when clicking outside
function closeSidebar() {
  if (isMobile.value) {
    sidebarOpen.value = false
  }
}

// Handle escape key
function handleEscape(e) {
  if (e.key === 'Escape' && sidebarOpen.value) {
    sidebarOpen.value = false
  }
}

// Lifecycle
onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
  document.addEventListener('keydown', handleEscape)
  // Load pending follow requests count
  loadPendingCount()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
  document.removeEventListener('keydown', handleEscape)
})

async function loadPendingCount() {
  try {
    const data = await json('/api/follows/pending/')
    pendingRequests.value = Array.isArray(data) ? data.length : 0
  } catch {
    pendingRequests.value = 0
  }
}
</script>

<template>
  <div class="app-shell" :class="{ 'sidebar-open': sidebarOpen }">
    <!-- Mobile Overlay -->
    <div
      v-if="isMobile && sidebarOpen"
      class="sidebar-overlay"
      @click="closeSidebar"
    ></div>

    <!-- Header -->
    <header class="app-header">
      <div class="header-left">
        <!-- Mobile Menu Button -->
        <button
          v-if="isMobile"
          @click="toggleSidebar"
          class="mobile-menu-btn"
          :class="{ 'active': sidebarOpen }"
          aria-label="Toggle navigation menu"
        >
          <span class="hamburger-line"></span>
          <span class="hamburger-line"></span>
          <span class="hamburger-line"></span>
        </button>

        <div class="brand">
          <strong class="brand-text">Trailium</strong>
        </div>
      </div>

      <div class="header-right">
        <UserMenu />
      </div>
    </header>

    <div class="app-main">
      <!-- Sidebar -->
      <aside
        class="app-sidebar"
        :class="{
          'sidebar-open': sidebarOpen,
          'sidebar-mobile': isMobile
        }"
      >
        <nav class="sidebar-nav">
          <RouterLink
            to="/"
            class="nav-link"
            active-class="is-active"
            @click="closeSidebar"
          >
            <span class="nav-icon">🏠</span>
            <span class="nav-text">Home</span>
          </RouterLink>

          <RouterLink
            to="/users"
            class="nav-link"
            active-class="is-active"
            @click="closeSidebar"
          >
            <span class="nav-icon">👥</span>
            <span class="nav-text">Users</span>
          </RouterLink>

          <RouterLink
            to="/todos"
            class="nav-link"
            active-class="is-active"
            @click="closeSidebar"
          >
            <span class="nav-icon">✅</span>
            <span class="nav-text">Todos</span>
          </RouterLink>

          <RouterLink
            to="/posts"
            class="nav-link"
            active-class="is-active"
            @click="closeSidebar"
          >
            <span class="nav-icon">📝</span>
            <span class="nav-text">Posts</span>
          </RouterLink>

          <RouterLink
            to="/albums"
            class="nav-link"
            active-class="is-active"
            @click="closeSidebar"
          >
            <span class="nav-icon">📸</span>
            <span class="nav-text">Albums</span>
          </RouterLink>

          <RouterLink
            to="/connections"
            class="nav-link"
            active-class="is-active"
            @click="closeSidebar"
          >
            <span class="nav-icon">🔗</span>
            <span class="nav-text">Connections</span>
            <span v-if="pendingRequests > 0" class="badge">{{ pendingRequests }}</span>
          </RouterLink>

          <!-- Development Tools (admin only) -->
          <div v-if="isAdmin" class="dev-section">
            <div class="dev-header">
              <div class="dev-badge">Dev Tools</div>
            </div>
            <RouterLink
              to="/cookie-test"
              class="nav-link dev-link"
              active-class="is-active"
              @click="closeSidebar"
            >
              <span class="nav-icon">🍪</span>
              <span class="nav-text">Cookie Test</span>
            </RouterLink>
          </div>

          <!-- Admin Only Links -->
          <div v-if="isAdmin" class="admin-section">
            <div class="admin-header">
              <div class="admin-badge">Admin Tools</div>
            </div>
            <RouterLink
              to="/admin-danger"
              class="nav-link admin-link"
              active-class="is-active"
              @click="closeSidebar"
            >
              <span class="nav-icon">⚠️</span>
              <span class="nav-text">Admin Danger</span>
            </RouterLink>
          </div>
        </nav>

        <!-- Bottom Section -->
        <div class="sidebar-bottom">
          <RouterLink
            to="/settings"
            class="nav-link"
            active-class="is-active"
            @click="closeSidebar"
          >
            <span class="nav-icon">⚙️</span>
            <span class="nav-text">Settings</span>
          </RouterLink>

          <!-- Brand Logo -->
          <div class="brand-logo">
            <img
              :src="logoSrc"
              alt="N2Mobil Logotype"
              class="logo-image"
            />
          </div>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="app-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: var(--c-bg);
  color: var(--c-text);
  display: flex;
  flex-direction: column;
}

/* Header Styles */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  border-bottom: 1px solid var(--c-border);
  background: var(--c-surface);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.mobile-menu-btn {
  display: none;
  flex-direction: column;
  justify-content: space-around;
  width: 30px;
  height: 30px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 200;
}

.hamburger-line {
  width: 100%;
  height: 3px;
  background: var(--c-text);
  border-radius: 2px;
  transition: all 0.3s ease;
  transform-origin: center;
}

.mobile-menu-btn.active .hamburger-line:nth-child(1) {
  transform: rotate(45deg) translate(6px, 6px);
}

.mobile-menu-btn.active .hamburger-line:nth-child(2) {
  opacity: 0;
}

.mobile-menu-btn.active .hamburger-line:nth-child(3) {
  transform: rotate(-45deg) translate(6px, -6px);
}

.brand {
  display: flex;
  align-items: center;
}

.brand-text {
  font-weight: 600;
  letter-spacing: 0.02em;
  font-size: 18px;
}

.header-right {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* Main Layout */
.app-main {
  display: flex;
  flex: 1;
  min-height: 0;
}

/* Sidebar Styles */
.app-sidebar {
  width: 240px;
  border-right: 1px solid var(--c-border);
  background: var(--c-surface);
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease;
  z-index: 150;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  overflow-y: auto;
}

.sidebar-nav {
  display: grid;
  gap: 4px;
  padding: 12px;
  flex: 1;
}

.nav-link {
  padding: 12px 14px;
  border-radius: 10px;
  color: var(--c-text-muted);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 12px;
  border-left: 3px solid transparent;
  transition: all 0.2s ease;
  font-size: 14px;
}

.nav-link:hover {
  background: var(--c-surface-2);
  color: var(--c-text);
  transform: translateX(4px);
}

.nav-link.is-active {
  background: var(--c-surface-2);
  color: var(--c-text);
  font-weight: 600;
  border-left-color: var(--c-accent);
}

.nav-icon {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.nav-text {
  flex: 1;
}

/* Admin Section */
.admin-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--c-border);
}

.admin-header {
  margin-bottom: 8px;
  padding: 8px 12px;
  background: #fef2f2;
  border-radius: 8px;
  border: 1px solid #fecaca;
}

.admin-badge {
  font-size: 12px;
  color: #991b1b;
  font-weight: 500;
}

.admin-link {
  color: #dc2626;
}

.admin-link:hover {
  background: #fef2f2;
}

.admin-link.is-active {
  background: #fef2f2;
  border-left-color: #dc2626;
}

/* Dev Section */
.dev-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--c-border);
}

.dev-header {
  margin-bottom: 8px;
  padding: 8px 12px;
  background: #f0f9ff;
  border-radius: 8px;
  border: 1px solid #bae6fd;
}

.dev-badge {
  font-size: 12px;
  color: #0369a1;
  font-weight: 500;
}

.dev-link {
  color: #0284c7;
}

.dev-link:hover {
  background: #f0f9ff;
}

.dev-link.is-active {
  background: #f0f9ff;
  border-left-color: #0284c7;
}

/* Sidebar Bottom */
.sidebar-bottom {
  padding: 12px;
  border-top: 1px solid var(--c-border);
  margin-top: auto;
}

.brand-logo {
  padding: 8px 4px;
  margin-top: 12px;
}

.logo-image {
  object-fit: contain;
  object-position: left;
  max-width: 100%;
  height: auto;
  display: block;
}

/* Main Content */
.app-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: var(--c-bg);
  margin-left: 240px;
}

/* Mobile Styles */
@media (max-width: 1023px) {
  .app-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    transform: translateX(-100%);
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  }

  .sidebar-open {
    transform: translateX(0);
  }

  .mobile-menu-btn {
    display: flex;
  }

  .sidebar-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 140;
  }

  .app-content {
    padding: 16px;
    margin-left: 0;
  }
}

@media (max-width: 767px) {
  .app-header {
    padding: 12px 16px;
  }

  .brand-text {
    font-size: 16px;
  }

  .app-content {
    padding: 12px;
    margin-left: 0;
  }

  .nav-link {
    padding: 14px 16px;
    font-size: 16px;
  }

  .nav-icon {
    font-size: 18px;
    width: 24px;
  }
}

/* Tablet Styles */
@media (min-width: 768px) and (max-width: 1023px) {
  .app-sidebar {
    width: 280px;
  }

  .app-content {
    padding: 20px;
    margin-left: 0;
  }
}

/* Animation for sidebar */
.sidebar-mobile {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Focus styles for accessibility */
.nav-link:focus {
  outline: 2px solid var(--c-accent);
  outline-offset: 2px;
}

.mobile-menu-btn:focus {
  outline: 2px solid var(--c-accent);
  outline-offset: 2px;
  border-radius: 4px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .app-sidebar {
    border-right-width: 2px;
  }

  .nav-link {
    border-left-width: 4px;
  }

  .admin-header {
    border-width: 2px;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .app-sidebar,
  .nav-link,
  .hamburger-line {
    transition: none;
  }
}
</style>
