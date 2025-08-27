<script setup>
import { ref, onMounted } from 'vue'
import { json } from '@/lib/http'

const testResults = ref([])
const loading = ref(false)

const addResult = (message, type = 'info') => {
  testResults.value.push({
    id: Date.now(),
    message,
    type,
    timestamp: new Date().toLocaleTimeString()
  })
}

const testCookieEndpoints = async () => {
  loading.value = true
  testResults.value = []

  try {
    // Test 1: Set cookies
    addResult('🧪 Testing SET cookies endpoint...', 'info')

    const setResponse = await json('/api/auth/set-cookies/', {
      method: 'POST',
      body: JSON.stringify({
        access: 'test_access_token_' + Date.now(),
        refresh: 'test_refresh_token_' + Date.now()
      })
    })

    addResult('✅ SET cookies endpoint working!', 'success')
    addResult(`Response: ${JSON.stringify(setResponse)}`, 'info')

    // Test 2: Clear cookies
    addResult('🧪 Testing CLEAR cookies endpoint...', 'info')

    const clearResponse = await json('/api/auth/clear-cookies/', {
      method: 'POST'
    })

    addResult('✅ CLEAR cookies endpoint working!', 'success')
    addResult(`Response: ${JSON.stringify(clearResponse)}`, 'info')

    // Test 3: Test with invalid data
    addResult('🧪 Testing validation with invalid data...', 'info')

    try {
      await json('/api/auth/set-cookies/', {
        method: 'POST',
        body: JSON.stringify({
          access: '',  // Empty access token
          refresh: 'test_refresh_token'
        })
      })
      addResult('❌ Validation failed - should have rejected empty token', 'error')
    } catch (error) {
      if (error.message.includes('Missing tokens')) {
        addResult('✅ Validation working - rejected empty access token!', 'success')
      } else {
        addResult(`❌ Unexpected error: ${error.message}`, 'error')
      }
    }

    // Test 4: Check browser cookies
    addResult('🧪 Checking browser cookies...', 'info')
    const cookies = document.cookie
    if (cookies) {
      addResult(`📋 Browser cookies: ${cookies}`, 'info')
    } else {
      addResult('📋 No browser cookies found', 'info')
    }

    addResult('🎉 All tests completed!', 'success')

  } catch (error) {
    addResult(`❌ Test failed: ${error.message}`, 'error')
    console.error('Cookie test error:', error)
  } finally {
    loading.value = false
  }
}

const clearResults = () => {
  testResults.value = []
}

onMounted(() => {
  addResult('🚀 Cookie Test Page Loaded', 'info')
  addResult('Click "Run Tests" to test cookie endpoints', 'info')
})
</script>

<template>
  <div class="cookie-test-page">
    <div class="test-header">
      <h1>🍪 Cookie Integration Test</h1>
      <p>Test the secure cookie system for JWT tokens</p>
    </div>

    <div class="test-controls">
      <button
        @click="testCookieEndpoints"
        :disabled="loading"
        class="test-btn primary"
      >
        {{ loading ? 'Running Tests...' : 'Run Tests' }}
      </button>

      <button
        @click="clearResults"
        class="test-btn secondary"
      >
        Clear Results
      </button>
    </div>

    <div class="test-results">
      <h3>Test Results</h3>

      <div v-if="testResults.length === 0" class="no-results">
        <p>No test results yet. Click "Run Tests" to start.</p>
      </div>

      <div v-else class="results-list">
        <div
          v-for="result in testResults"
          :key="result.id"
          class="result-item"
          :class="`result-${result.type}`"
        >
          <span class="result-timestamp">{{ result.timestamp }}</span>
          <span class="result-message">{{ result.message }}</span>
        </div>
      </div>
    </div>

    <div class="test-info">
      <h3>What This Tests</h3>
      <ul>
        <li>✅ SET cookies endpoint functionality</li>
        <li>✅ CLEAR cookies endpoint functionality</li>
        <li>✅ Input validation (empty tokens)</li>
        <li>✅ Browser cookie handling</li>
        <li>✅ Error handling</li>
      </ul>

      <h3>Expected Results</h3>
      <ul>
        <li>SET cookies should return success message</li>
        <li>CLEAR cookies should return success message</li>
        <li>Empty access token should be rejected</li>
        <li>All requests should complete without errors</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.cookie-test-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.test-header {
  text-align: center;
  margin-bottom: 32px;
}

.test-header h1 {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: var(--c-text);
}

.test-header p {
  font-size: 16px;
  color: var(--c-text-muted);
  margin: 0;
}

.test-controls {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 32px;
}

.test-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 120px;
}

.test-btn.primary {
  background: var(--c-accent);
  color: white;
}

.test-btn.primary:hover:not(:disabled) {
  background: var(--c-accent-dark, #7c3aed);
  transform: translateY(-1px);
}

.test-btn.secondary {
  background: var(--c-surface);
  color: var(--c-text);
  border: 2px solid var(--c-border);
}

.test-btn.secondary:hover {
  background: var(--c-surface-2);
  border-color: var(--c-accent);
}

.test-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.test-results {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
}

.test-results h3 {
  margin: 0 0 16px 0;
  font-size: 20px;
  color: var(--c-text);
}

.no-results {
  text-align: center;
  color: var(--c-text-muted);
  padding: 40px 20px;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-item {
  display: flex;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 6px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
}

.result-timestamp {
  color: var(--c-text-muted);
  font-size: 12px;
  min-width: 80px;
}

.result-message {
  flex: 1;
}

.result-info {
  background: rgba(59, 130, 246, 0.1);
  color: #1e40af;
}

.result-success {
  background: rgba(34, 197, 94, 0.1);
  color: #166534;
}

.result-error {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.test-info {
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
  border-radius: 12px;
  padding: 24px;
}

.test-info h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  color: var(--c-text);
}

.test-info ul {
  margin: 0 0 24px 0;
  padding-left: 20px;
}

.test-info li {
  margin-bottom: 8px;
  color: var(--c-text);
  line-height: 1.5;
}

.test-info li:last-child {
  margin-bottom: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .cookie-test-page {
    padding: 16px;
  }

  .test-header h1 {
    font-size: 24px;
  }

  .test-controls {
    flex-direction: column;
    align-items: center;
  }

  .test-btn {
    width: 100%;
    max-width: 200px;
  }

  .result-item {
    flex-direction: column;
    gap: 4px;
  }

  .result-timestamp {
    min-width: auto;
  }
}
</style>
