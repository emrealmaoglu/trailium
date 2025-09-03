/**
 * Albümler mağazası: albümler ve fotoğraflar; CRUD + sayfalama.
 */
import { defineStore } from 'pinia'
import { json } from '@/lib/http'

type Any = Record<string, any>

export const useAlbumsStore = defineStore('albums', {
  state: () => ({
    albums: [] as Any[],
    photosByAlbum: {} as Record<number, Any[]>,
    page: 1,
    pageSize: 10,
    count: 0,
    loading: false,
    error: null as string | null,
  }),
  getters: {
    totalPages: (s) => Math.max(1, Math.ceil(s.count / s.pageSize)),
  },
  actions: {
    /** Albümleri getirir */
    async fetchAlbums(userId: number, { page = 1, pageSize = 10 } = {}) {
      this.loading = true; this.error = null; this.page = page; this.pageSize = pageSize
      try {
        const data: any = await json(`/api/albums/?page=${page}&page_size=${pageSize}`)
        const arr = data?.results ?? data ?? []
        this.albums = arr.filter((a: Any) => (a.user?.id ?? a.author?.id) === userId || true)
        this.count = data?.count ?? this.albums.length
      } catch (e: any) { this.error = e?.message || 'fetchAlbums failed' }
      finally { this.loading = false }
    },
    async fetchPhotos(albumId: number) {
      const data: any = await json(`/api/albums/${albumId}/photos/`)
      this.photosByAlbum[albumId] = data ?? []
    },
    async createAlbum(payload: { title: string; visibility?: string }) {
      const data: any = await json(`/api/albums/`, { method: 'POST', body: JSON.stringify(payload) })
      this.albums.unshift(data)
    },
    async updateAlbum(id: number, payload: Any) {
      const data: any = await json(`/api/albums/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) })
      this.albums = this.albums.map(a => a.id === id ? data : a)
    },
    async deleteAlbum(id: number) {
      await json(`/api/albums/${id}/`, { method: 'DELETE' })
      this.albums = this.albums.filter(a => a.id !== id)
    },
    async addPhoto(albumId: number, payload: { title?: string; url?: string; file?: File }) {
      // For simplicity: URL-based upload (backend also supports file)
      const data: any = await json(`/api/albums/${albumId}/photos/`, { method: 'POST', body: JSON.stringify(payload) })
      const arr = this.photosByAlbum[albumId] ?? []
      this.photosByAlbum[albumId] = [data, ...arr]
    },
    async deletePhoto(albumId: number, photoId: number) {
      // Delete endpoint not implemented in backend helper; keeping client-only for now
      this.photosByAlbum[albumId] = (this.photosByAlbum[albumId]||[]).filter(p => p.id !== photoId)
    }
  }
})
