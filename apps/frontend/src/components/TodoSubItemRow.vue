<template>
  <div class="sub">
    <label class="ck">
      <input type="checkbox" :checked="subitem.is_done" @change="$emit('toggle', subitem)" :aria-label="subitem.title" />
    </label>
    <div class="title" :class="{ done: subitem.is_done }">{{ subitem.title }}</div>
    <button class="del" @click="$emit('delete', subitem)" :aria-label="$t('todos.delete') as string">×</button>
  </div>
</template>

<script setup lang="ts">
defineProps<{ subitem: any }>()
defineEmits(['toggle','delete'])
</script>

<style scoped>
.sub { display: grid; grid-template-columns: 24px 1fr 24px; align-items: center; gap: 8px; }
.ck { display: grid; place-items: center; }
.title.done { text-decoration: line-through; color: var(--c-text-muted); }
.del { border: 1px solid var(--c-border); background: var(--c-surface-2); border-radius: 6px; width: 24px; height: 24px; line-height: 1; }
</style>


