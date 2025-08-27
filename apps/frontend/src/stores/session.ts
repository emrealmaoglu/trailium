import { defineStore } from 'pinia'
import { json } from '@/lib/http'

type Me = {
  id: number
  username: string
  email?: string
  is_superuser?: boolean
}

export const useSessionStore = defineStore('session', {
  state: () => ({
    access: '' as string,
    refresh: '' as string,
    user: null as Me | null,
    rememberMe: true as boolean,
    idleTimer: 0 as any,
    isRefreshing: false as boolean,
  }),
  getters: {
    isAuthenticated: (state) => !!state.user && !!state.access,
    isLoggedIn: (state) => !!state.user && !!state.access,
    displayName: (state) => state.user?.username || 'User',
    displayEmail: (state) => state.user?.email || '',
    initials: (state) => (state.user?.username || '?').slice(0, 1).toUpperCase(),
  },
  actions: {
    // Secure token storage using httpOnly cookies
    async setSecureTokens(access: string, refresh: string) {
      try {
        // Set httpOnly cookies via backend endpoint
        await json('/api/auth/set-cookies/', {
          method: 'POST',
          body: JSON.stringify({ access, refresh })
        })
        this.access = access
        this.refresh = refresh
      } catch (error) {
        console.error('Failed to set secure tokens:', error)
        throw new Error('Failed to set secure authentication tokens')
      }
    },

    async clearSecureTokens() {
      try {
        // Clear cookies via backend endpoint
        await json('/api/auth/clear-cookies/', { method: 'POST' })
      } catch (error) {
        console.error('Failed to clear secure tokens:', error)
      } finally {
        this.access = ''
        this.refresh = ''
      }
    },

    loadFromStorage() {
      // Only store non-sensitive preferences in localStorage
      try {
        const raw = localStorage.getItem('userPreferences')
        if (raw) {
          const data = JSON.parse(raw)
          this.rememberMe = data.rememberMe ?? true
        }
      } catch (error) {
        console.error('Failed to load user preferences:', error)
        this.rememberMe = true
      }
    },

    saveToStorage() {
      // Only store non-sensitive preferences
      try {
        localStorage.setItem('userPreferences', JSON.stringify({
          rememberMe: this.rememberMe
        }))
      } catch (error) {
        console.error('Failed to save user preferences:', error)
      }
    },

    async register(payload: { username: string; password: string; email?: string }) {
      // Add password strength validation
      if (payload.password.length < 8) {
        throw new Error('Password must be at least 8 characters long')
      }
      if (!/[A-Z]/.test(payload.password)) {
        throw new Error('Password must contain at least one uppercase letter')
      }
      if (!/[a-z]/.test(payload.password)) {
        throw new Error('Password must contain at least one lowercase letter')
      }
      if (!/\d/.test(payload.password)) {
        throw new Error('Password must contain at least one number')
      }

      try {
        await json('/api/auth/register/', { method: 'POST', body: JSON.stringify(payload) })
      } catch (error) {
        console.error('Registration failed:', error)
        throw error
      }
    },

    async login(payload: { username: string; password: string; rememberMe?: boolean }) {
      try {
        const data = await json<{ access: string; refresh: string }>('/api/auth/login/', {
          method: 'POST',
          body: JSON.stringify(payload)
        })

        this.rememberMe = !!payload.rememberMe
        await this.setSecureTokens(data.access, data.refresh)
        this.saveToStorage()
        await this.fetchMe()

        // Set appropriate idle timeout based on security level
        const timeout = this.rememberMe ? 8 * 60 * 60 * 1000 : 30 * 60 * 1000 // 8 hours vs 30 minutes
        this.startIdleTimer(timeout)
      } catch (error) {
        console.error('Login failed:', error)
        throw error
      }
    },

    async refreshToken() {
      if (!this.refresh || this.isRefreshing) return false

      this.isRefreshing = true
      try {
        const data = await json<{ access: string }>('/api/auth/refresh/', {
          method: 'POST',
          body: JSON.stringify({ refresh: this.refresh })
        })

        await this.setSecureTokens(data.access, this.refresh)
        this.saveToStorage()
        return true
      } catch (error) {
        console.error('Token refresh failed:', error)
        // Refresh failed, force logout
        await this.logout()
        return false
      } finally {
        this.isRefreshing = false
      }
    },

    async fetchMe() {
      try {
        this.user = await json<Me>('/api/users/me/')
      } catch (error) {
        console.error('Failed to fetch user data:', error)
        this.user = null
        // If user fetch fails, try to refresh token
        if (this.refresh) {
          const refreshed = await this.refreshToken()
          if (refreshed) {
            await this.fetchMe()
          }
        }
      }
    },

    async logout() {
      try {
        await this.clearSecureTokens()
      } catch (error) {
        console.error('Failed to clear secure tokens during logout:', error)
      }

      this.access = ''
      this.refresh = ''
      this.user = null

      try {
        localStorage.removeItem('userPreferences')
      } catch (error) {
        console.error('Failed to clear local storage during logout:', error)
      }

      if (typeof window !== 'undefined') {
        window.location.href = '/auth/login'
      }
    },

    startIdleTimer(ms = 30 * 60 * 1000) {
      clearTimeout(this.idleTimer)
      this.idleTimer = setTimeout(() => {
        this.logout()
      }, ms)

      // Reset timer on user activity
      const resetTimer = () => {
        clearTimeout(this.idleTimer)
        this.idleTimer = setTimeout(() => this.logout(), ms)
      }

      const events = ['click', 'keydown', 'mousemove', 'scroll', 'touchstart']
      events.forEach(evt =>
        window.addEventListener(evt, resetTimer, { passive: true })
      )
    },

    initIdleTimerOnLoad() {
      if (this.access) {
        const timeout = this.rememberMe ? 8 * 60 * 60 * 1000 : 30 * 60 * 1000
        this.startIdleTimer(timeout)
      }
    }
  },
})
