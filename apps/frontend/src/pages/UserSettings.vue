<template>
  <div class="settings-page">
    <h3 class="title">{{ $t('settings.title') }}</h3>
    <div v-if="store.loading" class="skl"></div>
    <SettingsForm v-else :me="store.me" :loading="store.loading" :error="store.error" @save="onSave" />
  </div>
</template>

<script setup lang="ts">
/** Kullanıcı ayarları sekmesi. */
import { onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import SettingsForm from '@/components/SettingsForm.vue'

const store = useSettingsStore()
onMounted(() => store.fetchMe())

async function onSave(payload: any) { await store.updateMe(payload) }
</script>

<style scoped>
.settings-page { display: grid; gap: 12px; max-width: 720px; }
.title { margin: 0; font-size: 18px; font-weight: 700; }
.skl { height: 100px; border-radius: 10px; background: var(--c-surface-2); animation: pulse 1.2s ease-in-out infinite; }
@keyframes pulse { 0%{opacity:.6} 50%{opacity:.95} 100%{opacity:.6} }
</style>


