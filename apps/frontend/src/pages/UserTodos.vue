<template>
  <div class="todos-page">
    <div class="left">
      <div v-if="loadingLists" class="skl"></div>
      <TodoListPicker
        v-else
        :lists="store.lists"
        v-model="store.listId"
        @create="onCreateList"
      />
      <div v-if="!loadingLists && store.lists.length === 0" class="empty">{{ t('todos.emptyLists') }}</div>
    </div>

    <div class="right">
      <div v-if="store.loading" class="loading">
        <div class="spinner"></div>
        <p>{{ t('todos.items') }}…</p>
      </div>

      <template v-else>
        <header class="hdr" v-if="store.currentList">
          <h3>{{ store.currentList.name }}</h3>
          <span class="muted">{{ t('todos.progress') }}:</span>
          <ProgressBar :value="store.currentList.progress ?? store.currentList.progress_cached ?? 0" />
        </header>

        <div class="add-line">
          <input v-model="newItem" :placeholder="t('todos.addItem') as string" class="inp" @keydown.enter="onCreateItem" />
          <button class="btn" @click="onCreateItem">+</button>
        </div>

        <div v-if="store.items.length === 0" class="empty">{{ t('todos.emptyItems') }}</div>

        <div class="items">
          <TodoItemRow
            v-for="it in store.items"
            :key="it.id"
            :item="it"
            :subitems="store.subitems[it.id]"
            @toggle="onToggle(it.id)"
          />
        </div>

        <Pagination
          :page="store.page"
          :total-pages="store.totalPages"
          :disabled="store.loading"
          @update:page="onChangePage"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTodosStore } from '@/stores/todos'
import TodoListPicker from '@/components/TodoListPicker.vue'
import TodoItemRow from '@/components/TodoItemRow.vue'
import Pagination from '@/components/Pagination.vue'
import ProgressBar from '@/components/ProgressBar.vue'
import { useI18n } from 'vue-i18n'

const route = useRoute(); const router = useRouter(); const { t } = useI18n()
const store = useTodosStore()
const loadingLists = ref(true)
const newItem = ref('')

const userId = Number(route.params.id)

onMounted(async () => {
  await store.fetchLists(userId, { page: 1, pageSize: 10 })
  loadingLists.value = false
  if (store.listId) {
    const p = Number(route.query.page ?? 1) || 1
    await store.fetchItems(store.listId, { page: p, pageSize: store.pageSize })
  }
})

watch(() => store.listId, async (id) => {
  if (id) await store.fetchItems(id, { page: 1, pageSize: store.pageSize })
})

function onChangePage(p: number) {
  if (!store.listId) return
  store.fetchItems(store.listId, { page: p, pageSize: store.pageSize })
  router.push({ query: { ...route.query, page: String(p) } })
}

async function onCreateList(name: string) {
  await store.createList({ name })
}

async function onCreateItem() {
  const title = newItem.value.trim(); if (!title || !store.listId) return
  await store.createItem({ list: store.listId, title })
  newItem.value = ''
}

const onToggle = (id: number) => () => store.toggleItemDone(id)
</script>

<style scoped>
.todos-page { display: grid; grid-template-columns: 280px 1fr; gap: 16px; }
.left { border-right: 1px solid var(--c-border); padding-right: 12px; }
.right { padding-left: 4px; display: grid; gap: 12px; }
.loading { display: grid; place-items: center; min-height: 120px; }
.empty { color: var(--c-text-muted); font-size: 14px; }
.hdr { display: grid; grid-template-columns: auto auto 1fr; gap: 8px; align-items: center; }
.add-line { display: flex; gap: 8px; }
.inp { flex: 1; border: 1px solid var(--c-border); border-radius: 8px; padding: 8px 10px; }
.btn { border: 1px solid var(--c-border); background: var(--c-surface); border-radius: 8px; padding: 8px 10px; }
.items { display: grid; gap: 8px; }
.skl { width: 100%; height: 120px; border-radius: 10px; background: var(--c-surface-2); animation: pulse 1.2s ease-in-out infinite; }
@keyframes pulse { 0%{opacity:.6} 50%{opacity:.95} 100%{opacity:.6} }
</style>
