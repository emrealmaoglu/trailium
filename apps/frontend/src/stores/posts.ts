/**
 * Gönderiler mağazası: postlar, yorumlar, beğeniler; CRUD + sayfalama.
 */
import { defineStore } from 'pinia'
import { json } from '@/lib/http'

type Any = Record<string, any>

export const usePostsStore = defineStore('posts', {
  state: () => ({
    posts: [] as Any[],
    commentsByPost: {} as Record<number, Any[]>,
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
    /** Gönderileri getir (gerekirse istemci tarafı filtre uygular) */
    async fetchPosts(userId: number, { page = 1, pageSize = 10 } = {}) {
      this.loading = true; this.error = null; this.page = page; this.pageSize = pageSize
      try {
        const data: any = await json(`/api/posts/?page=${page}&page_size=${pageSize}`)
        const arr = data?.results ?? data ?? []
        // İstemci tarafı kullanıcı filtresi
        this.posts = arr.filter((p: Any) => (p.author?.id ?? p.user?.id) === userId)
        this.count = data?.count ?? this.posts.length
      } catch (e: any) { this.error = e?.message || 'fetchPosts failed' }
      finally { this.loading = false }
    },
    async fetchComments(postId: number) {
      const data: any = await json(`/api/posts/${postId}/comments/`)
      this.commentsByPost[postId] = data ?? []
    },
    async createPost(payload: { title: string; body?: string }) {
      const data: any = await json(`/api/posts/`, { method: 'POST', body: JSON.stringify(payload) })
      this.posts.unshift(data)
    },
    async updatePost(id: number, payload: Any) {
      const data: any = await json(`/api/posts/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) })
      this.posts = this.posts.map(p => p.id === id ? data : p)
    },
    async deletePost(id: number) {
      await json(`/api/posts/${id}/`, { method: 'DELETE' })
      this.posts = this.posts.filter(p => p.id !== id)
    },
    async like(id: number) {
      try {
        await json(`/api/posts/${id}/like/`, { method: 'POST' })
        this.posts = this.posts.map(p => p.id === id ? { ...p, likes_count: (p.likes_count||0)+1 } : p)
      } catch {}
    },
    async unlike(id: number) {
      try {
        await json(`/api/posts/${id}/unlike/`, { method: 'DELETE' })
        this.posts = this.posts.map(p => p.id === id ? { ...p, likes_count: Math.max(0, (p.likes_count||0)-1) } : p)
      } catch {}
    },
    async addComment(postId: number, body: string) {
      await json(`/api/posts/${postId}/comments/`, { method: 'POST', body: JSON.stringify({ body }) })
      await this.fetchComments(postId)
    },
    async deleteComment(postId: number, commentId: number) {
      // Backend doesn't expose delete under nested in current code; skip for now or implement when available
      this.commentsByPost[postId] = (this.commentsByPost[postId]||[]).filter(c => c.id !== commentId)
    }
  }
})
