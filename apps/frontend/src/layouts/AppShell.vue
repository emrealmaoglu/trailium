<script setup>
import { useRoute, useRouter } from 'vue-router'
import logoSrc from '../assets/brand/N2Mobil-Logotype.png'

const router = useRouter()
const route  = useRoute()

const nav = [
  { to: '/',       label: 'Users'  },
  { to: '/todos',  label: 'Todos'  },
  { to: '/posts',  label: 'Posts'  },
  { to: '/albums', label: 'Albums' },
]
</script>

<template>
  <div class="min-h-screen grid grid-cols-[240px_1fr] relative">
    <!-- Sidebar -->
    <aside class="bg-white border-r border-brand-grayLight relative">
      <div class="px-5 py-4 flex items-center gap-2">
        <div class="w-9 h-9 rounded-full overflow-hidden shrink-0">
          <img :src="logoSrc" class="w-full h-full object-cover object-left" alt="N2Mobil" />
        </div>
        <strong class="ml-1 text-sm tracking-wide text-title">Trailium</strong>
      </div>

      <nav class="mt-3 space-y-1">
        <button
          v-for="item in nav"
          :key="item.to"
          @click="router.push(item.to)"
          class="w-full text-left px-5 py-2.5 text-sm rounded-md hover:bg-brand.grayLight/50 transition"
          :class="route.path === item.to ? 'bg-brand.grayLight/70 font-medium' : 'text-brand-gray2'"
        >
          {{ item.label }}
        </button>
      </nav>

      <!-- Alt köşe logo alanı -->
      <div class="absolute bottom-4 left-0 right-0 px-5">
        <div class="h-12 rounded-xl bg-brand.grayLight/60 flex items-center justify-center text-xs text-brand-gray2">
          N2Mobil
        </div>
      </div>
    </aside>

    <!-- İçerik sütunu -->
    <section class="min-h-screen bg-[var(--surface)]">
      <!-- Topbar -->
      <header class="h-14 bg-white border-b border-brand-grayLight flex items-center px-6">
        <span class="text-sm text-subtitle">Topbar</span>
      </header>

      <!-- Sayfa içeriği -->
      <main class="max-w-7xl mx-auto">
        <router-view />
      </main>
    </section>
  </div>
</template>


