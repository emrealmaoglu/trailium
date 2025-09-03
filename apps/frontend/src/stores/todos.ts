/**
 * Todos mağazası: listeler, öğeler, alt öğeler; CRUD + sayfalama.
 */
import { defineStore } from 'pinia'
import { json } from '@/lib/http'

type Id = number
type AnyRecord = Record<string, any>

export const useTodosStore = defineStore('todos', {
  state: () => ({
    lists: [] as AnyRecord[],
    items: [] as AnyRecord[],
    subitems: {} as Record<Id, AnyRecord[]>,
    listId: null as Id | null,
    page: 1,
    pageSize: 10,
    count: 0,
    loading: false,
    error: null as string | null,
  }),
  getters: {
    totalPages: (s): number => Math.max(1, Math.ceil(s.count / s.pageSize)),
    currentList: (s): AnyRecord | null => s.lists.find((l:any) => l.id === s.listId) || null,
  },
  actions: {
    /** Kullanıcının listelerini getirir */
    async fetchLists(userId: number, { page = 1, pageSize = 10 } = {}) {
      this.loading = true; this.error = null
      try {
        const data: any = await json(`/api/todo-lists/?user=${userId}&page=${page}&page_size=${pageSize}`)
        this.lists = data?.results ?? data ?? []
        if (!this.listId && this.lists.length) this.listId = this.lists[0].id
      } catch (e: any) { this.error = e?.message || 'fetchLists failed' }
      finally { this.loading = false }
    },
    /** Aktif listedeki item’ları getirir */
    async fetchItems(listId: number, { page = 1, pageSize = 10 } = {}) {
      this.loading = true; this.error = null; this.page = page; this.pageSize = pageSize
      try {
        const data: any = await json(`/api/todo-items/?list=${listId}&page=${page}&page_size=${pageSize}`)
        const arr = data?.results ?? data ?? []
        // Sunucu filtrasyonu yoksa istemci tarafı filtre uygula
        this.items = arr.filter((i:any) => (i.list?.id ?? i.list) === listId)
        this.count = (data?.count ?? this.items.length)
      } catch (e: any) { this.error = e?.message || 'fetchItems failed' }
      finally { this.loading = false }
    },
    async fetchSubitems(itemId: number) {
      try {
        const data: any = await json(`/api/todo-subitems/?parent=${itemId}`)
        this.subitems[itemId] = data?.results ?? data ?? []
      } catch {/* sessizce geç */}
    },
    async createList(payload: { name: string; kind?: string; description?: string; }) {
      const data: any = await json(`/api/todo-lists/`, { method: 'POST', body: JSON.stringify(payload) })
      this.lists.unshift(data)
      if (!this.listId) this.listId = data.id
    },
    async updateList(id:number, payload:any) {
      const data: any = await json(`/api/todo-lists/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) })
      this.lists = this.lists.map(l => l.id === id ? data : l)
    },
    async deleteList(id:number) {
      await json(`/api/todo-lists/${id}/`, { method: 'DELETE' })
      this.lists = this.lists.filter(l => l.id !== id)
      if (this.listId === id) this.listId = this.lists[0]?.id ?? null
    },
    async createItem(payload: { list: number; title: string; description?: string; due_date?: string; }) {
      const data: any = await json(`/api/todo-items/`, { method: 'POST', body: JSON.stringify(payload) })
      this.items.unshift(data)
    },
    async updateItem(id:number, payload:any) {
      const data: any = await json(`/api/todo-items/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) })
      this.items = this.items.map(i => i.id === id ? data : i)
    },
    async deleteItem(id:number) {
      await json(`/api/todo-items/${id}/`, { method: 'DELETE' })
      this.items = this.items.filter(i => i.id !== id)
    },
    async toggleItemDone(id:number) {
      const before = this.items.slice()
      this.items = this.items.map(i => i.id === id ? { ...i, is_done: !i.is_done } : i)
      try {
        const data: any = await json(`/api/todo-items/${id}/toggle-done/`, { method: 'POST' })
        this.items = this.items.map(i => i.id === id ? data : i)
      } catch {
        this.items = before
      }
    },
    async createSubItem(payload: { parent: number; title: string; description?: string; }) {
      const data: any = await json(`/api/todo-subitems/`, { method: 'POST', body: JSON.stringify(payload) })
      const arr = this.subitems[payload.parent] ?? []
      this.subitems[payload.parent] = [data, ...arr]
    },
    async updateSubItem(id:number, payload:any, parent:number) {
      const data: any = await json(`/api/todo-subitems/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) })
      this.subitems[parent] = (this.subitems[parent] ?? []).map(s => s.id === id ? data : s)
    },
    async deleteSubItem(id:number, parent:number) {
      await json(`/api/todo-subitems/${id}/`, { method: 'DELETE' })
      this.subitems[parent] = (this.subitems[parent] ?? []).filter(s => s.id !== id)
    },
  }
})
