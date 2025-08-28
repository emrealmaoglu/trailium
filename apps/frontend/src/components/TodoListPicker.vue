<template>
  <div class="picker">
    <div class="add">
      <input v-model="newName" :placeholder="$t('todos.addList') as string" class="inp" @keydown.enter="add" />
      <button class="btn" @click="add">+</button>
    </div>
    <ul class="list">
      <li v-for="l in lists" :key="l.id">
        <button :class="['row', { active: l.id === modelValue } ]" @click="$emit('update:modelValue', l.id)" :aria-label="l.name">
          <div class="name">{{ l.name }}</div>
          <ProgressBar :value="l.progress ?? l.progress_cached ?? 0" />
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ProgressBar from './ProgressBar.vue'

defineProps<{ lists: any[]; modelValue: number | null }>()
const emit = defineEmits<{ 'update:modelValue':[number|null], 'create':[string] }>()
const newName = ref('')

function add() {
  const name = newName.value.trim()
  if (!name) return
  emit('create', name)
  newName.value = ''
}
</script>

<style scoped>
.picker { display: flex; flex-direction: column; gap: 8px; }
.add { display: flex; gap: 8px; }
.inp { flex: 1; border: 1px solid var(--c-border); border-radius: 8px; padding: 8px 10px; }
.btn { border: 1px solid var(--c-border); background: var(--c-surface); border-radius: 8px; padding: 8px 10px; }
.list { display: flex; flex-direction: column; gap: 8px; margin: 0; padding: 0; list-style: none; }
.row { width: 100%; text-align: left; border: 1px solid var(--c-border); border-radius: 10px; padding: 10px; background: var(--c-surface); }
.row.active { outline: 2px solid var(--c-accent); outline-offset: 2px; }
.name { font-weight: 600; margin-bottom: 6px; }
</style>


