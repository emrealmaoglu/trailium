<template>
  <div class="admin-danger-page">
    <Breadcrumbs />

    <div class="page-header">
      <h1 class="page-title">🚨 Admin Danger Zone</h1>
      <p class="page-subtitle">Critical administrative operations - use with extreme caution</p>
    </div>

    <!-- Admin Status Check -->
    <div v-if="!isAdmin" class="admin-check">
      <div class="alert alert-error">
        <h3>❌ Access Denied</h3>
        <p>This page is only accessible to superusers. You do not have the required permissions.</p>
        <router-link to="/" class="btn btn-primary">Go Home</router-link>
      </div>
    </div>

    <!-- Admin Tools -->
    <div v-else class="admin-tools">
      <!-- Cookie Test Tool -->
      <div class="admin-tool-section">
        <h2>🍪 Cookie Test Tool</h2>
        <p class="tool-description">
          Test and manage cookies for development and debugging purposes.
        </p>

        <div class="cookie-test-controls">
          <div class="cookie-input-group">
            <label for="cookie-name">Cookie Name:</label>
            <input
              id="cookie-name"
              v-model="cookieName"
              type="text"
              placeholder="cookie_name"
              class="cookie-input"
            />
          </div>

          <div class="cookie-input-group">
            <label for="cookie-value">Cookie Value:</label>
            <input
              id="cookie-value"
              v-model="cookieValue"
              type="text"
              placeholder="cookie_value"
              class="cookie-input"
            />
          </div>

          <div class="cookie-input-group">
            <label for="cookie-days">Expiry (days):</label>
            <input
              id="cookie-days"
              v-model="cookieDays"
              type="number"
              min="1"
              max="365"
              class="cookie-input"
            />
          </div>

          <div class="cookie-actions">
            <button @click="setCookie" class="btn-set-cookie">Set Cookie</button>
            <button @click="getCookie" class="btn-get-cookie">Get Cookie</button>
            <button @click="deleteCookie" class="btn-delete-cookie">Delete Cookie</button>
            <button @click="listAllCookies" class="btn-list-cookies">List All Cookies</button>
          </div>
        </div>

        <div v-if="cookieResult" class="cookie-result">
          <h4>Result:</h4>
          <pre>{{ cookieResult }}</pre>
        </div>
      </div>

      <!-- Purge Non-Admin Users -->
      <div class="danger-zone">
        <h2>🗑️ Purge Non-Admin Users</h2>
        <p class="warning-text">
          <strong>⚠️ DANGER:</strong> This operation will permanently delete ALL non-admin users and their content.
          This action cannot be undone!
        </p>

        <!-- Dry Run Results -->
        <div v-if="dryRunResults" class="dry-run-results">
          <h3>🔍 Dry Run Results</h3>
          <div class="results-grid">
            <div class="result-item">
              <span class="result-label">Users to Delete:</span>
              <span class="result-value">{{ dryRunResults.users }}</span>
            </div>
            <div class="result-item">
              <span class="result-label">Posts:</span>
              <span class="result-value">{{ dryRunResults.posts }}</span>
            </div>
            <div class="result-item">
              <span class="result-label">Comments:</span>
              <span class="result-value">{{ dryRunResults.comments }}</span>
            </div>
            <div class="result-item">
              <span class="result-label">Likes:</span>
              <span class="result-value">{{ dryRunResults.likes }}</span>
            </div>
            <div class="result-item">
              <span class="result-label">Albums:</span>
              <span class="result-value">{{ dryRunResults.albums }}</span>
            </div>
            <div class="result-item">
              <span class="result-label">Photos:</span>
              <span class="result-value">{{ dryRunResults.photos }}</span>
            </div>
            <div class="result-item">
              <span class="result-label">Todo Lists:</span>
              <span class="result-value">{{ dryRunResults.todo_lists }}</span>
            </div>
            <div class="result-item">
              <span class="result-label">Total Objects:</span>
              <span class="result-value">{{ dryRunResults.total_related }}</span>
            </div>
          </div>
        </div>

        <!-- Keep List Input -->
        <div class="keep-list-section">
          <h3>🛡️ Users to Preserve</h3>
          <p>Enter usernames or emails of users you want to keep (in addition to superusers):</p>
          <div class="keep-input-group">
            <input
              v-model="newKeepUser"
              @keyup.enter="addKeepUser"
              type="text"
              placeholder="Username or email"
              class="keep-input"
            />
            <button @click="addKeepUser" class="btn btn-secondary">Add</button>
          </div>
          <div v-if="keepList.length > 0" class="keep-list">
            <div v-for="(user, index) in keepList" :key="index" class="keep-item">
              <span>{{ user }}</span>
              <button @click="removeKeepUser(index)" class="btn-remove">×</button>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="action-buttons">
          <button @click="runDryRun" class="btn btn-info" :disabled="isLoading">
            🔍 Run Dry Run
          </button>
          <button @click="showPurgeModal" class="btn btn-danger" :disabled="isLoading || !dryRunResults">
            🗑️ Execute Purge
          </button>
        </div>
      </div>
    </div>

    <!-- Purge Confirmation Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>🚨 Confirm Purge Operation</h3>
          <button @click="closeModal" class="modal-close">×</button>
        </div>

        <div class="modal-body">
          <div class="warning-box">
            <h4>⚠️ FINAL WARNING</h4>
            <p>You are about to permanently delete:</p>
            <ul>
              <li><strong>{{ dryRunResults?.users || 0 }} users</strong></li>
              <li><strong>{{ dryRunResults?.total_related || 0 }} related objects</strong></li>
            </ul>
            <p>This action <strong>CANNOT BE UNDONE</strong>!</p>
          </div>

          <div class="confirmation-input">
            <label for="confirm-text">Type exactly "PURGE_NON_ADMIN_USERS" to confirm:</label>
            <input
              id="confirm-text"
              v-model="confirmationText"
              type="text"
              placeholder="PURGE_NON_ADMIN_USERS"
              class="confirm-input"
            />
          </div>

          <div class="keep-summary">
            <h4>Users that will be preserved:</h4>
            <ul>
              <li>All superusers (is_superuser=True)</li>
              <li v-for="user in keepList" :key="user">{{ user }}</li>
            </ul>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeModal" class="btn btn-secondary">Cancel</button>
          <button
            @click="executePurge"
            class="btn btn-danger"
            :disabled="confirmationText !== 'PURGE_NON_ADMIN_USERS' || isExecuting"
          >
            {{ isExecuting ? 'Executing...' : 'Execute Purge' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-content">
        <Spinner size="large" />
        <p>Processing...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { json } from '@/lib/http'
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import Spinner from '@/components/Spinner.vue'

const router = useRouter()
const sessionStore = useSessionStore()

// Reactive data
const isLoading = ref(false)
const isExecuting = ref(false)
const showModal = ref(false)
const confirmationText = ref('')
const dryRunResults = ref(null)
const keepList = ref([])
const newKeepUser = ref('')

// Cookie test variables
const cookieName = ref('')
const cookieValue = ref('')
const cookieDays = ref(7)
const cookieResult = ref('')

// Computed
const isAdmin = computed(() => sessionStore.user?.is_superuser)

// Methods
function addKeepUser() {
  if (newKeepUser.value.trim() && !keepList.value.includes(newKeepUser.value.trim())) {
    keepList.value.push(newKeepUser.value.trim())
    newKeepUser.value = ''
  }
}

function removeKeepUser(index) {
  keepList.value.splice(index, 1)
}

async function runDryRun() {
  if (!isAdmin.value) return

  isLoading.value = true
  try {
    const response = await json('/api/admin-tools/purge-non-admin-users/', {
      method: 'POST',
      body: {
        confirm: 'PURGE_NON_ADMIN_USERS',
        keep: keepList.value,
        dry_run: true
      }
    })

    dryRunResults.value = response.would_delete
    showNotification('Dry run completed successfully', 'success')
  } catch (error) {
    console.error('Dry run failed:', error)
    showNotification('Dry run failed: ' + (error.message || 'Unknown error'), 'error')
  } finally {
    isLoading.value = false
  }
}

function showPurgeModal() {
  if (!dryRunResults.value) {
    showNotification('Please run a dry run first', 'warning')
    return
  }
  showModal.value = true
  confirmationText.value = ''
}

function closeModal() {
  showModal.value = false
  confirmationText.value = ''
}

async function executePurge() {
  if (confirmationText.value !== 'PURGE_NON_ADMIN_USERS') {
    showNotification('Please type the exact confirmation text', 'warning')
    return
  }

  isExecuting.value = true
  try {
    const response = await json('/api/admin-tools/purge-non-admin-users/', {
      method: 'POST',
      body: {
        confirm: 'PURGE_NON_ADMIN_USERS',
        keep: keepList.value,
        dry_run: false
      }
    })

    showNotification('Purge completed successfully', 'success')
    closeModal()

    // Clear results and refresh
    dryRunResults.value = null

    // Redirect to users page to see the results
    router.push('/users')
  } catch (error) {
    console.error('Purge failed:', error)
    showNotification('Purge failed: ' + (error.message || 'Unknown error'), 'error')
  } finally {
    isExecuting.value = false
  }
}

// Cookie test functions
function setCookie() {
  if (!cookieName.value.trim()) {
    showNotification('Please enter a cookie name', 'warning')
    return
  }

  const expires = new Date()
  expires.setDate(expires.getDate() + (cookieDays.value || 7))

  document.cookie = `${cookieName.value}=${cookieValue.value}; expires=${expires.toUTCString()}; path=/`

  cookieResult.value = `Cookie "${cookieName.value}" set successfully!\nExpires: ${expires.toLocaleString()}`
  showNotification('Cookie set successfully', 'success')
}

function getCookie() {
  if (!cookieName.value.trim()) {
    showNotification('Please enter a cookie name', 'warning')
    return
  }

  const nameEQ = cookieName.value + "="
  const ca = document.cookie.split(';')

  for (let i = 0; i < ca.length; i++) {
    let c = ca[i]
    while (c.charAt(0) === ' ') c = c.substring(1, c.length)
    if (c.indexOf(nameEQ) === 0) {
      const value = c.substring(nameEQ.length, c.length)
      cookieResult.value = `Cookie "${cookieName.value}" found!\nValue: ${value}`
      return
    }
  }

  cookieResult.value = `Cookie "${cookieName.value}" not found`
  showNotification('Cookie not found', 'warning')
}

function deleteCookie() {
  if (!cookieName.value.trim()) {
    showNotification('Please enter a cookie name', 'warning')
    return
  }

  document.cookie = `${cookieName.value}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/`

  cookieResult.value = `Cookie "${cookieName.value}" deleted successfully!`
  showNotification('Cookie deleted successfully', 'success')
}

function listAllCookies() {
  const cookies = document.cookie.split(';')
  if (cookies.length === 0 || (cookies.length === 1 && cookies[0].trim() === '')) {
    cookieResult.value = 'No cookies found'
    return
  }

  const cookieList = cookies.map(cookie => {
    const [name, value] = cookie.trim().split('=')
    return `${name}: ${value || '(no value)'}`
  }).join('\n')

  cookieResult.value = `All Cookies:\n${cookieList}`
  showNotification('Cookies listed successfully', 'success')
}

// Notifications
function showNotification(message, type = 'info') {
  // Use the global notification system if available
  if (window.showNotification) {
    window.showNotification(message, type)
  } else {
    alert(`${type.toUpperCase()}: ${message}`)
  }
}

// Lifecycle
onMounted(() => {
  if (!isAdmin.value) {
    router.push('/')
  }
})
</script>

<style scoped>
.admin-danger-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--c-text);
  margin-bottom: 10px;
}

.page-subtitle {
  font-size: 1.1rem;
  color: var(--c-text-muted);
}

.admin-check {
  margin: 40px 0;
}

.alert {
  padding: 20px;
  border-radius: 12px;
  border: 1px solid;
}

.alert-error {
  background: #fef2f2;
  border-color: #fecaca;
  color: #991b1b;
}

.admin-tools {
  margin-top: 30px;
}

/* Cookie Test Tool */
.admin-tool-section {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 30px;
}

.tool-description {
  color: var(--c-text-muted);
  margin-bottom: 20px;
}

.cookie-test-controls {
  display: grid;
  gap: 16px;
  margin-bottom: 20px;
}

.cookie-input-group {
  display: grid;
  gap: 8px;
}

.cookie-input-group label {
  font-weight: 500;
  color: var(--c-text);
}

.cookie-input {
  padding: 10px 12px;
  border: 1px solid var(--c-border);
  border-radius: 8px;
  background: var(--c-surface);
  color: var(--c-text);
  font-size: 14px;
}

.cookie-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-set-cookie, .btn-get-cookie, .btn-delete-cookie, .btn-list-cookies {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-set-cookie {
  background: #10b981;
  color: white;
}

.btn-set-cookie:hover {
  background: #059669;
}

.btn-get-cookie {
  background: #3b82f6;
  color: white;
}

.btn-get-cookie:hover {
  background: #2563eb;
}

.btn-delete-cookie {
  background: #ef4444;
  color: white;
}

.btn-delete-cookie:hover {
  background: #dc2626;
}

.btn-list-cookies {
  background: #8b5cf6;
  color: white;
}

.btn-list-cookies:hover {
  background: #7c3aed;
}

.cookie-result {
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
  border-radius: 8px;
  padding: 16px;
  margin-top: 20px;
}

.cookie-result h4 {
  margin: 0 0 12px 0;
  color: var(--c-text);
}

.cookie-result pre {
  background: var(--c-bg);
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--c-text);
  font-family: monospace;
  font-size: 13px;
  margin: 0;
}

.danger-zone {
  background: var(--c-surface);
  border: 2px solid #ef4444;
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 30px;
}

.danger-zone h2 {
  color: #ef4444;
  margin-bottom: 20px;
  font-size: 1.8rem;
}

.warning-text {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 25px;
  color: #991b1b;
}

.dry-run-results {
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 25px;
}

.dry-run-results h3 {
  margin-bottom: 15px;
  color: var(--c-text);
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: var(--c-bg);
  border-radius: 8px;
  border: 1px solid var(--c-border);
}

.result-label {
  font-weight: 500;
  color: var(--c-text);
}

.result-value {
  font-weight: 700;
  color: var(--c-accent);
  font-size: 1.1rem;
}

.keep-list-section {
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 25px;
}

.keep-list-section h3 {
  margin-bottom: 15px;
  color: var(--c-text);
}

.keep-input-group {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.keep-input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid var(--c-border);
  border-radius: 8px;
  background: var(--c-bg);
  color: var(--c-text);
}

.keep-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.keep-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--c-accent);
  color: white;
  border-radius: 20px;
  font-size: 0.9rem;
}

.btn-remove {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.btn-remove:hover {
  background: rgba(255, 255, 255, 0.2);
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 1rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-info {
  background: #3b82f6;
  color: white;
}

.btn-info:hover:not(:disabled) {
  background: #2563eb;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #4b5563;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: 16px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--c-border);
}

.modal-header h3 {
  margin: 0;
  color: #ef4444;
  font-size: 1.5rem;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s ease;
  color: var(--c-text-muted);
}

.modal-close:hover {
  background: var(--c-surface-2);
}

.modal-body {
  padding: 24px;
}

.warning-box {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  color: #991b1b;
}

.warning-box h4 {
  margin: 0 0 15px 0;
  color: #dc2626;
}

.warning-box ul {
  margin: 10px 0;
  padding-left: 20px;
}

.confirmation-input {
  margin-bottom: 20px;
}

.confirmation-input label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--c-text);
}

.confirm-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--c-border);
  border-radius: 8px;
  background: var(--c-bg);
  color: var(--c-text);
  font-size: 1rem;
  font-family: monospace;
}

.confirm-input:focus {
  outline: none;
  border-color: var(--c-accent);
}

.keep-summary {
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
  border-radius: 8px;
  padding: 15px;
}

.keep-summary h4 {
  margin: 0 0 10px 0;
  color: var(--c-text);
}

.keep-summary ul {
  margin: 0;
  padding-left: 20px;
  color: var(--c-text-muted);
}

.modal-footer {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  padding: 20px 24px;
  border-top: 1px solid var(--c-border);
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
}

.loading-content {
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: 16px;
  padding: 30px;
  text-align: center;
}

.loading-content p {
  margin-top: 15px;
  color: var(--c-text);
  font-weight: 500;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-danger-page {
    padding: 15px;
  }

  .page-title {
    font-size: 2rem;
  }

  .danger-zone {
    padding: 20px;
  }

  .results-grid {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
  }

  .modal-content {
    width: 95%;
    margin: 20px;
  }
}
</style>
