<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M21 10.5C21 16 12 22 12 22S3 16 3 10.5a9 9 0 1 1 18 0Z"/><circle cx="12" cy="10.5" r="3"/>
  </svg>
</template>
<script setup>
defineProps({ size: { type: [Number,String], default: 18 } })
</script>
