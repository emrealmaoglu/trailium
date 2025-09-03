<script setup>
import IconPin from './icons/IconPin.vue'
import IconBuilding from './icons/IconBuilding.vue'
import IconGlobe from './icons/IconGlobe.vue'
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import { json } from '@/lib/http'

const props = defineProps({
  user: {
    type: Object, required: true,
    // expected shape: { id, name, email, phone, addressText, companyName, website, is_premium, is_private }
  }
})

const router = useRouter()
const goToDetail = () => {
  if (props.user && props.user.id != null) router.push(`/users/${props.user.id}/todos`)
}

const initial = (name) => (name || '?').trim().charAt(0).toUpperCase()

const followStatus = ref('unknown') // unknown|following|pending|none
const followBusy = ref(false)

async function toggleFollow(e) {
  e.stopPropagation()
  if (!props.user?.id || followBusy.value) return
  followBusy.value = true
  try {
    if (followStatus.value === 'following' || followStatus.value === 'pending') {
      await json(`/api/follows/users/${props.user.id}/unfollow/`, { method: 'POST' })
      followStatus.value = 'none'
    } else {
      await json(`/api/follows/users/${props.user.id}/follow/`, { method: 'POST' })
      // For private accounts, status will be 'pending' until approved
      // For public accounts, status will be 'following' immediately
      followStatus.value = props.user.is_private ? 'pending' : 'following'
    }
  } catch {
    // noop
  } finally {
    followBusy.value = false
  }
}

// Check current follow status on mount
onMounted(async () => {
  if (!props.user?.id) return
  try {
    const response = await json(`/api/follows/users/${props.user.id}/status/`)
    followStatus.value = response.status || 'none'
  } catch {
    followStatus.value = 'none'
  }
})
</script>

<template>
  <article class="card" style="padding:18px; cursor:pointer;" tabindex="0" role="button" @click="goToDetail">
    <header style="display:flex; gap:12px; align-items:center;">
      <div style="position: relative;">
        <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#ff4db0,#4db2ff);display:grid;place-items:center;color:#fff;font-weight:600;">
          {{ initial(user.name) }}
        </div>
        <!-- Premium badge -->
        <div v-if="user.is_premium" style="position: absolute; top: -4px; right: -4px; width: 20px; height: 20px; background: linear-gradient(135deg, #ffd700, #ffb347); border-radius: 50%; display: grid; place-items: center; font-size: 10px; color: #000; font-weight: bold; border: 2px solid var(--c-bg);">
          ⭐
        </div>
      </div>
      <div style="min-width:0;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="font-weight:600;">{{ user.name }}</span>
          <!-- Private account indicator -->
          <span v-if="user.is_private" style="font-size: 12px; color: var(--c-text-muted);">🔒</span>
        </div>
        <div style="color:var(--c-text-muted); font-size:13px; line-height:1.5;">
          {{ user.email }} · {{ user.phone }}
        </div>
      </div>
      <button @click="toggleFollow" :disabled="followBusy" style="margin-left:auto; border:1px solid var(--c-border); background:var(--c-surface); color:var(--c-text); border-radius:10px; padding:6px 10px; cursor:pointer; font-size:12px; transition: all 0.2s ease;">
        <span v-if="followBusy">...</span>
        <span v-else-if="followStatus==='following'">✓ Following</span>
        <span v-else-if="followStatus==='pending'">📩 Requested</span>
        <span v-else>{{ user.is_private ? '🔒 Request' : '➕ Follow' }}</span>
      </button>
    </header>

    <div class="rule"></div>

    <div style="display:grid; gap:8px; font-size:13px; color:var(--c-text-muted);">
      <div v-if="user.addressText" style="display:flex; gap:6px; align-items:center;">
        <IconPin style="width:14px; height:14px; opacity:.6;" />
        <span>{{ user.addressText }}</span>
      </div>
      <div v-if="user.companyName" style="display:flex; gap:6px; align-items:center;">
        <IconBuilding style="width:14px; height:14px; opacity:.6;" />
        <span>{{ user.companyName }}</span>
      </div>
      <div v-if="user.website" style="display:flex; gap:6px; align-items:center;">
        <IconGlobe style="width:14px; height:14px; opacity:.6;" />
        <span>{{ user.website }}</span>
      </div>
    </div>
  </article>
</template>
