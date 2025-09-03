import { defineStore } from 'pinia'
import { json } from '@/lib/http'

type Me = {
  id: number
  username: string
  email?: string
}

function decodeJwt(token: string): any | null {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join(''))
    return JSON.parse(jsonPayload)
  } catch {
    return null
  }
}

function isExpired(token: string): boolean {
  const payload = decodeJwt(token)
  if (!payload?.exp) return true
  const now = Math.floor(Date.now() / 1000)
  return payload.exp <= now
}

export const useSessionStore = defineStore('session', {
  state: () => ({
    access: '' as string,
    refresh: '' as string,
    user: null as Me | null,
    rememberMe: true as boolean,
    idleTimer: 0 as any,
  }),
  getters: {
    isAuthenticated: (state) => !!state.user && !!state.access,
    isLoggedIn: (state) => !!state.user && !!state.access,
    displayName: (state) => state.user?.username || 'User',
    displayEmail: (state) => state.user?.email || '',
    initials: (state) => (state.user?.username || '?').slice(0, 1).toUpperCase(),
  },
  actions: {
    loadFromStorage() {
      try {
        const raw = localStorage.getItem('session')
        if (raw) {
          const data = JSON.parse(raw)
          this.access = data.access || ''
          this.refresh = data.refresh || ''
          this.rememberMe = data.rememberMe ?? true
        }
      } catch {}
    },
    async initFromStorage() {
      this.loadFromStorage()
      if (!this.access) {
        this.user = null
        return
      }
      // Drop expired access; attempt refresh if refresh exists
      if (isExpired(this.access)) {
        if (this.refresh) {
          const refreshed = await this.refreshToken().catch(() => false)
          if (!refreshed) {
            this.access = ''
            this.refresh = ''
            this.user = null
            localStorage.removeItem('session')
            return
          }
        } else {
          this.access = ''
          this.user = null
          localStorage.removeItem('session')
          return
        }
      }
      // Fetch user to validate token server-side too
      try {
        this.user = await json<Me>('/api/users/me/')
      } catch {
        this.user = null
        // If server rejects token, clear
        this.access = ''
        if (!this.rememberMe) localStorage.removeItem('session')
      }
    },
    saveToStorage() {
      if (this.rememberMe) {
        localStorage.setItem('session', JSON.stringify({
          access: this.access,
          refresh: this.refresh,
          rememberMe: this.rememberMe
        }))
      } else {
        localStorage.removeItem('session')
      }
    },
    async register(payload: { username: string; password: string; email?: string }) {
      await json('/api/auth/register/', { method: 'POST', body: JSON.stringify(payload) })
    },
    async login(payload: { username: string; password: string; rememberMe?: boolean }) {
      const data = await json<{ access: string; refresh: string }>('/api/auth/login/', { method: 'POST', body: JSON.stringify(payload) })
      this.access = data.access
      this.refresh = data.refresh
      this.rememberMe = !!payload.rememberMe
      this.saveToStorage()
      await this.fetchMe()
      this.startIdleTimer(this.rememberMe ? 12 * 60 * 60 * 1000 : 30 * 60 * 1000)
    },
    async refreshToken() {
      if (!this.refresh) return false
      try {
        const data = await json<{ access: string }>('/api/auth/refresh/', { method: 'POST', body: JSON.stringify({ refresh: this.refresh }) })
        this.access = data.access
        this.saveToStorage()
        return true
      } catch {
        return false
      }
    },
    async fetchMe() {
      try {
        this.user = await json<Me>('/api/users/me/')
      } catch (error) {
        this.user = null
      }
    },
    async logout() {
      try {
        if (this.refresh) {
          await json('/api/auth/logout/', { method: 'POST', body: JSON.stringify({ refresh: this.refresh }) })
        }
      } catch {}
      this.access = ''
      this.refresh = ''
      this.user = null
      localStorage.removeItem('session')
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/login'
      }
    },
    startIdleTimer(ms = 30 * 60 * 1000) {
      clearTimeout(this.idleTimer)
      this.idleTimer = setTimeout(() => { this.logout() }, ms)
      ;['click','keydown','mousemove','scroll','touchstart'].forEach(evt => window.addEventListener(evt, () => { clearTimeout(this.idleTimer); this.idleTimer = setTimeout(() => this.logout(), ms) }, { passive: true }))
    },
    initIdleTimerOnLoad() {
      if (this.access) this.startIdleTimer(this.rememberMe ? 12 * 60 * 60 * 1000 : 30 * 60 * 1000)
    }
  },
})
