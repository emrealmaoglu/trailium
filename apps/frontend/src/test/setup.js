import { vi } from 'vitest'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = localStorageMock

// Mock fetch
global.fetch = vi.fn()

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  warn: vi.fn(),
  error: vi.fn(),
}

// Setup global test utilities
global.testUtils = {
  // Helper to create mock user data
  createMockUser: (overrides = {}) => ({
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    full_name: 'Test User',
    is_premium: false,
    is_private: false,
    avatar: '',
    about: '',
    created_at: '2025-01-01T00:00:00Z',
    ...overrides
  }),

  // Helper to create mock post data
  createMockPost: (overrides = {}) => ({
    id: 1,
    title: 'Test Post',
    body: 'This is a test post body',
    user: {
      id: 1,
      username: 'testuser'
    },
    likes_count: 0,
    comments_count: 0,
    created_at: '2025-01-01T00:00:00Z',
    ...overrides
  }),

  // Helper to wait for next tick
  nextTick: () => new Promise(resolve => setTimeout(resolve, 0)),

  // Helper to wait for specific time
  waitFor: (ms) => new Promise(resolve => setTimeout(resolve, ms)),
}
