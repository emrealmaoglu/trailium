<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { json } from '@/lib/http'

const loading = ref(true)
const errorMsg = ref('')
const lists = ref([])
const selectedListId = ref(null)

const selectedList = computed(() => lists.value.find(l => l.id === selectedListId.value))

async function fetchLists() {
  loading.value = true
  errorMsg.value = ''
  try {
    const payload = await json('/api/todos/lists/')
    const data = Array.isArray(payload) ? payload : payload.results || []
    lists.value = data
    if (lists.value.length > 0) selectedListId.value = lists.value[0].id
    if (lists.value.length === 0) errorMsg.value = 'No todos yet.'
  } catch (e) {
    errorMsg.value = 'Could not load todos.'
  } finally {
    loading.value = false
  }
}

async function toggleItem(item) {
  try {
    const updated = await json(`/api/todos/items/${item.id}/toggle-done/`, { method: 'POST' })
    const list = selectedList.value
    const idx = list.items.findIndex(i => i.id === item.id)
    if (idx !== -1) list.items[idx] = updated
    await refreshSelectedList()
  } catch (e) {
  }
}

async function toggleSub(sub) {
  try {
    const updated = await json(`/api/todos/subitems/${sub.id}/`, {
      method: 'PATCH',
      body: JSON.stringify({ is_done: !sub.is_done })
    })
    const list = selectedList.value
    for (const it of list.items) {
      const sidx = it.subitems.findIndex(s => s.id === sub.id)
      if (sidx !== -1) {
        it.subitems[sidx] = updated
        break
      }
    }
    await refreshSelectedList()
  } catch (e) {}
}

async function refreshSelectedList() {
  if (!selectedListId.value) return
  const data = await json(`/api/todos/lists/${selectedListId.value}/`)
  const idx = lists.value.findIndex(l => l.id === selectedListId.value)
  if (idx !== -1) lists.value[idx] = data
}

onMounted(() => {
  fetchLists()
  const onVis = () => { if (document.visibilityState === 'visible') fetchLists() }
  document.addEventListener('visibilitychange', onVis)
  onUnmounted(() => document.removeEventListener('visibilitychange', onVis))
})
</script>

<template>
  <div class="container">
    <div style="display:flex; align-items:center; gap:8px; margin:0 0 16px;">
      <h2 style="margin:0; font-size:22px; font-weight:700;">Todos</h2>
      <button @click="fetchLists" style="margin-left:auto; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:6px 10px; cursor:pointer; font-size:13px;">Refresh</button>
    </div>

    <div v-if="loading" class="card" style="padding:16px;">Loading…</div>
    <div v-else-if="errorMsg" class="card" style="padding:16px; color:var(--c-text-muted);">{{ errorMsg }}</div>
    <template v-else>
      <div class="card" style="padding:12px; display:flex; gap:8px; align-items:center;">
        <label for="listSel" style="font-size:14px; color:var(--c-text-muted);">List:</label>
        <select id="listSel" v-model.number="selectedListId" @change="refreshSelectedList" style="background:var(--c-surface); color:var(--c-text); border:1px solid var(--c-border); border-radius:10px; padding:6px 10px;">
          <option v-for="l in lists" :key="l.id" :value="l.id">{{ l.name }}</option>
        </select>
        <div v-if="selectedList" style="margin-left:auto; font-size:13px; color:var(--c-text-muted);">
          Progress: {{ selectedList.progress_cached || 0 }}%
        </div>
      </div>

      <div v-if="selectedList" class="card" style="padding:16px; margin-top:12px;">
        <div style="height:8px; background:var(--c-surface-2); border-radius:8px; overflow:hidden;">
          <div :style="{ width: (selectedList.progress_cached||0) + '%', height:'100%', background:'var(--c-accent)' }"></div>
        </div>

        <ul style="list-style:none; padding:0; margin:16px 0 0; display:grid; gap:10px;">
          <li v-for="it in selectedList.items" :key="it.id" class="card" style="padding:12px;">
            <label style="display:flex; gap:10px; align-items:flex-start; cursor:pointer;">
              <input type="checkbox" :checked="it.is_done" @change="toggleItem(it)" />
              <div>
                <div :style="{ textDecoration: it.is_done ? 'line-through' : 'none', fontWeight: 600 }">{{ it.title }}</div>
                <div style="color:var(--c-text-muted); font-size:13px;">{{ it.description }}</div>
              </div>
              <div style="margin-left:auto; font-size:12px; color:var(--c-text-muted);">{{ it.progress_cached }}%</div>
            </label>
            <ul v-if="it.subitems && it.subitems.length" style="list-style:none; padding-left:28px; margin-top:8px; display:grid; gap:6px;">
              <li v-for="s in it.subitems" :key="s.id" style="display:flex; gap:10px; align-items:center;">
                <input type="checkbox" :checked="s.is_done" @change="toggleSub(s)" />
                <div :style="{ textDecoration: s.is_done ? 'line-through' : 'none' }">{{ s.title }}</div>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </template>
  </div>
</template>
