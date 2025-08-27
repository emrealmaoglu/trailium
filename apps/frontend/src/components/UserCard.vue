<script setup>
import IconPin from './icons/IconPin.vue'
import IconBuilding from './icons/IconBuilding.vue'
import IconGlobe from './icons/IconGlobe.vue'

defineProps({
  user: {
    type: Object, required: true,
    // expected shape: { name, email, phone, addressText, companyName, website }
  }
})

const initial = (name) => (name || '?').trim().charAt(0).toUpperCase()
</script>

<template>
  <article class="card" style="padding:18px;" tabindex="0">
    <header style="display:flex; gap:12px; align-items:center;">
      <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#ff4db0,#4db2ff);display:grid;place-items:center;color:#fff;font-weight:600;">
        {{ initial(user.name) }}
      </div>
      <div style="min-width:0;">
        <div style="font-weight:600;">{{ user.name }}</div>
        <div style="color:var(--muted); font-size:13px; line-height:1.5;">
          {{ user.email }} · {{ user.phone }}
        </div>
      </div>
    </header>

    <div class="rule"></div>

    <section style="display:grid;gap:12px;">
      <div style="display:flex; gap:10px; align-items:flex-start;">
        <IconPin />
        <div>
          <div style="font-weight:600; font-size:13px; margin-bottom:2px; color:var(--muted);">Location</div>
          <div style="font-size:14px; white-space:pre-line;">{{ user.addressText }}</div>
        </div>
      </div>

      <div style="display:flex; gap:10px; align-items:flex-start;">
        <IconBuilding />
        <div>
          <div style="font-weight:600; font-size:13px; margin-bottom:2px; color:var(--muted);">Company</div>
          <div style="font-size:14px;">{{ user.companyName }}</div>
        </div>
      </div>

      <div style="display:flex; gap:10px; align-items:flex-start;">
        <IconGlobe />
        <div>
          <div style="font-weight:600; font-size:13px; margin-bottom:2px; color:var(--muted);">Website</div>
          <a :href="`https://${user.website}`" target="_blank" rel="noreferrer" :aria-label="`Open website for ${user.name}`" style="font-size:14px;">
            {{ user.website }}
          </a>
        </div>
      </div>
    </section>
  </article>
</template>


