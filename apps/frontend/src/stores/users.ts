/**
 * Kullanıcı listesi mağazası (Pinia).
 * Sayfalama durumunu ve kullanıcı listesini yönetir.
 */
import { defineStore } from 'pinia'
import { json } from '@/lib/http'

type UserItem = {
  id: number
  username: string
  full_name?: string
  avatar?: string
}

export const useUsersStore = defineStore('users', {
  state: () => ({
    users: [] as UserItem[],
    page: 1,
    pageSize: 10,
    count: 0,
    loading: false,
    error: null as string | null,
    q: '' as string,
  }),
  getters: {
    totalPages: (state) => Math.max(1, Math.ceil(state.count / state.pageSize)),
  },
  actions: {
    /**
     * Kullanıcı listesini getirir.
     * @param opts - sayfa ve sayfa boyutu
     */
    async fetchUsers(opts: { page?: number; pageSize?: number } = {}) {
      // Türkçe: Yükleniyor durumunu başlat
      this.loading = true
      this.error = null
      const page = opts.page ?? this.page
      const pageSize = opts.pageSize ?? this.pageSize
      try {
        const data = await json<{ results: any[]; count: number }>(`/api/users/?page=${page}&page_size=${pageSize}`)
        this.users = (data.results || []).map((u: any) => ({
          id: u.id,
          username: u.username,
          full_name: u.full_name,
          avatar: u.avatar,
        }))
        this.count = data.count || this.users.length
        this.page = page
        this.pageSize = pageSize
      } catch (err: any) {
        // Türkçe: Hata mesajını sakla
        this.error = err?.message || 'Failed to load users'
      } finally {
        this.loading = false
      }
    },
  },
})


