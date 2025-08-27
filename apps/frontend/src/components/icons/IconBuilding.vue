<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M3 22h18"/><path d="M6 22V5l6-2v19"/><path d="M18 22V9h-6"/><path d="M9 8h2M9 12h2M9 16h2M15 12h2M15 16h2"/>
  </svg>
</template>
<script setup>
defineProps({ size: { type: [Number,String], default: 18 } })
</script>


