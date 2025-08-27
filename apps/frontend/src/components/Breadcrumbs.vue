<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const breadcrumbs = computed(() => {
  const paths = route.path.split('/').filter(Boolean)
  const items = []

  let currentPath = ''

  // Add home
  items.push({
    name: 'Home',
    path: '/',
    icon: '🏠'
  })

  // Add each path segment
  paths.forEach((path, index) => {
    currentPath += `/${path}`

    // Convert path to readable name
    let name = path.charAt(0).toUpperCase() + path.slice(1)
    let icon = '📁'

    // Customize names and icons for specific routes
    switch (path) {
      case 'users':
        icon = '👥'
        name = 'Users'
        break
      case 'todos':
        icon = '✅'
        name = 'Todos'
        break
      case 'posts':
        icon = '📝'
        name = 'Posts'
        break
      case 'albums':
        icon = '📸'
        name = 'Albums'
        break
      case 'feed':
        icon = '🔄'
        name = 'Feed'
        break
      case 'settings':
        icon = '⚙️'
        name = 'Settings'
        break
      case 'auth':
        icon = '🔐'
        name = 'Authentication'
        break
    }

    // Check if this is a dynamic route (like user ID)
    if (path.match(/^\d+$/)) {
      icon = '👤'
      name = 'User Profile'
    }

    items.push({
      name,
      path: currentPath,
      icon,
      isLast: index === paths.length - 1
    })
  })

  return items
})

function navigateTo(path) {
  if (path !== route.path) {
    router.push(path)
  }
}
</script>

<template>
  <nav v-if="breadcrumbs.length > 1" class="breadcrumbs" aria-label="Breadcrumb navigation">
    <ol class="breadcrumbs-list">
      <li v-for="(item, index) in breadcrumbs" :key="item.path" class="breadcrumb-item">
        <button
          v-if="!item.isLast"
          @click="navigateTo(item.path)"
          class="breadcrumb-link"
          :title="`Go to ${item.name}`"
        >
          <span class="breadcrumb-icon">{{ item.icon }}</span>
          <span class="breadcrumb-text">{{ item.name }}</span>
        </button>
        <span v-else class="breadcrumb-current">
          <span class="breadcrumb-icon">{{ item.icon }}</span>
          <span class="breadcrumb-text">{{ item.name }}</span>
        </span>
        <span v-if="index < breadcrumbs.length - 1" class="breadcrumb-separator">/</span>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
.breadcrumbs {
  margin-bottom: 20px;
  padding: 12px 16px;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 10px;
}

.breadcrumbs-list {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.breadcrumb-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: none;
  border: none;
  color: var(--c-text-muted);
  text-decoration: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
}

.breadcrumb-link:hover {
  background: var(--c-surface-2);
  color: var(--c-text);
  transform: translateY(-1px);
}

.breadcrumb-current {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  color: var(--c-text);
  font-weight: 500;
  font-size: 13px;
}

.breadcrumb-icon {
  font-size: 14px;
}

.breadcrumb-text {
  font-size: 13px;
}

.breadcrumb-separator {
  color: var(--c-text-muted);
  font-size: 12px;
  font-weight: 300;
}

@media (max-width: 768px) {
  .breadcrumbs {
    padding: 8px 12px;
    margin-bottom: 16px;
  }

  .breadcrumb-text {
    display: none;
  }

  .breadcrumb-link,
  .breadcrumb-current {
    padding: 6px 8px;
  }
}
</style>
