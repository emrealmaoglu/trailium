<template>
  <form class="form" @submit.prevent="onSave">
    <label class="row">
      <span>{{ $t('settings.name') }}</span>
      <input v-model="model.full_name" class="inp" />
    </label>
    <label class="row">
      <span>{{ $t('settings.email') }}</span>
      <input v-model="model.email" type="email" class="inp" />
    </label>
    <label class="row">
      <span>{{ $t('settings.visibility') }}</span>
      <select v-model="model.visibility" class="inp">
        <option value="public">{{ $t('user.tabs.posts') }} – Public</option>
        <option value="followers">Followers</option>
        <option value="private">Private</option>
      </select>
    </label>
    <label class="row">
      <span>{{ $t('settings.private') }}</span>
      <input type="checkbox" v-model="model.is_private" />
    </label>
    <label class="row">
      <span>{{ $t('settings.premium') }}</span>
      <input type="checkbox" v-model="model.is_premium" />
    </label>
    <div class="actions">
      <button class="btn" :disabled="loading">{{ $t('settings.save') }}</button>
      <span v-if="ok" class="ok">{{ $t('settings.success') }}</span>
      <span v-if="error" class="err">{{ $t('settings.error') }}</span>
    </div>
  </form>
</template>

<script setup lang="ts">
/** Ayar formu: kullanıcı kendi profilini günceller. */
import { reactive, ref, watch } from 'vue'
const props = defineProps<{ me: any; loading?: boolean; error?: string|null }>()
const emit = defineEmits<{ 'save':[any] }>()
const model = reactive<any>({ full_name:'', email:'', visibility:'public', is_private:false, is_premium:false })
const ok = ref(false)

watch(() => props.me, (v) => { if (v) Object.assign(model, { full_name:v.full_name, email:v.email, visibility:v.visibility||'public', is_private:!!v.is_private, is_premium:!!v.is_premium }) }, { immediate: true })

async function onSave() {
  ok.value = false
  await emit('save', { full_name:model.full_name, email:model.email, visibility:model.visibility, is_private:model.is_private, is_premium:model.is_premium })
  ok.value = true
  setTimeout(()=> ok.value=false, 1500)
}
</script>

<style scoped>
.form { display: grid; gap: 12px; }
.row { display: grid; grid-template-columns: 180px 1fr; align-items: center; gap: 8px; }
.inp { border: 1px solid var(--c-border); border-radius: 8px; padding: 8px 10px; }
.actions { display: flex; gap: 8px; align-items: center; }
.btn { border: 1px solid var(--c-border); background: var(--c-accent); color: #fff; border-radius: 8px; padding: 8px 12px; }
.ok { color: #16a34a; font-size: 13px; }
.err { color: #dc2626; font-size: 13px; }
</style>
