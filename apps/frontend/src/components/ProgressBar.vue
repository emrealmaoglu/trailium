<template>
  <div class="bar" role="progressbar" :aria-valuenow="value" aria-valuemin="0" aria-valuemax="100">
    <div class="fill" :style="{ width: value + '%' }"></div>
    <span class="label">{{ value }}%</span>
  </div>
  </template>

<script setup lang="ts">
defineProps<{ value: number }>()
</script>

<style scoped>
.bar { position: relative; height: 10px; border-radius: 999px; background: var(--c-surface-2); overflow: hidden; }
.fill { height: 100%; background: var(--c-accent); }
.label { position: absolute; top: -20px; right: 0; font-size: 12px; color: var(--c-text-muted); }
</style>
