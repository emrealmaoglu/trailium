import { defineStore } from 'pinia'
import { json } from '@/lib/http'

type Me = {
  id: number
  username: string
  email?: string
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
    displayName: (state) => state.user?.username || 'User',
    displayEmail: (state) => state.user?.email || '',
    initials: (state) => (state.user?.username || '?').slice(0, 1).toUpperCase(),
  },
  actions: {
    loadFromStorage() {
      try {
        const raw = localStorage.getItem('session')
        if (raw) Object.assign(this, JSON.parse(raw))
      } catch {}
    },
    saveToStorage() {
      if (this.rememberMe) localStorage.setItem('session', JSON.stringify({ access: this.access, refresh: this.refresh, rememberMe: this.rememberMe }))
      else localStorage.removeItem('session')
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
      this.user = await json<Me>('/api/users/me/')
    },
    async logout() {
      try { if (this.refresh) await json('/api/auth/logout/', { method: 'POST', body: JSON.stringify({ refresh: this.refresh }) }) } catch {}
      this.access = ''
      this.refresh = ''
      this.user = null
      localStorage.removeItem('session')
      if (typeof window !== 'undefined') {
        const url = new URL(window.location.href)
        const isOnAuth = url.pathname.startsWith('/auth')
        if (!isOnAuth) {
          const redirect = encodeURIComponent(url.pathname + url.search)
          window.location.replace(`/auth/login?redirect=${redirect}`)
        }
      }
    },
    startIdleTimer(ms = 30 * 60 * 1000) {
      clearTimeout(this.idleTimer)
      this.idleTimer = setTimeout(() => { this.logout() }, ms)
      ;['click','keydown','mousemove','scroll','touchstart'].forEach(evt => window.addEventListener(evt, () => { clearTimeout(this.idleTimer); this.idleTimer = setTimeout(() => this.logout(), ms) }, { passive: true }))
    },
  },
})

