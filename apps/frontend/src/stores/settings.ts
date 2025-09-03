/**
 * Ayarlar mağazası: /api/users/me/ için getirme ve güncelleme.
 */
import { defineStore } from 'pinia'
import { json } from '@/lib/http'

export const useSettingsStore = defineStore('settings', {
  state: () => ({ me: null as any, loading: false, error: null as string|null }),
  actions: {
    async fetchMe() {
      this.loading = true; this.error = null
      try { this.me = await json('/api/users/me/') } catch (e:any) { this.error = e?.message || 'fetchMe failed' } finally { this.loading = false }
    },
    async updateMe(payload: any) {
      this.loading = true; this.error = null
      try { this.me = await json('/api/users/me/', { method: 'PATCH', body: JSON.stringify(payload) }) } catch (e:any) { this.error = e?.message || 'updateMe failed' } finally { this.loading = false }
    }
  }
})
