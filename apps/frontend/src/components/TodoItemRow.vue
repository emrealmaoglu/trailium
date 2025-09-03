<template>
  <div class="row">
    <label class="ck">
      <input type="checkbox" :checked="item.is_done" @change="$emit('toggle', item.id)" :aria-label="item.title" />
    </label>
    <div class="main">
      <div class="title" :class="{ done: item.is_done }">{{ item.title }}</div>
      <div v-if="item.due_date" class="due">{{ $t('todos.due') }}: {{ item.due_date }}</div>
      <ProgressBar v-if="item.subitems?.length" :value="item.progress_cached || 0" />
      <div class="subs" v-if="subitems?.length">
        <TodoSubItemRow v-for="s in subitems" :key="s.id" :subitem="s" @toggle="$emit('toggle-sub', s)" @delete="$emit('delete-sub', s)" />
      </div>
    </div>
    <div class="actions">
      <button class="btn" @click="$emit('edit', item)">{{ $t('todos.edit') }}</button>
      <button class="btn" @click="$emit('delete', item)">{{ $t('todos.delete') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import ProgressBar from './ProgressBar.vue'
import TodoSubItemRow from './TodoSubItemRow.vue'

defineProps<{ item: any; subitems?: any[] }>()
defineEmits(['toggle','edit','delete','toggle-sub','delete-sub'])
</script>

<style scoped>
.row { display: grid; grid-template-columns: 28px 1fr auto; gap: 10px; align-items: start; border: 1px solid var(--c-border); border-radius: 10px; padding: 10px; background: var(--c-surface); }
.ck { display: grid; place-items: center; }
.title { font-weight: 600; }
.title.done { text-decoration: line-through; color: var(--c-text-muted); }
.due { font-size: 12px; color: var(--c-text-muted); }
.actions { display: flex; gap: 6px; }
.btn { border: 1px solid var(--c-border); border-radius: 8px; padding: 6px 8px; background: var(--c-surface-2); }
.subs { margin-top: 8px; display: grid; gap: 6px; }
</style>
