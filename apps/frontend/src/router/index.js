import { createRouter, createWebHistory } from 'vue-router'
import { useSessionStore } from '@/stores/session'

const routes = [
  {
    path: '/',
    redirect: '/feed',
    meta: { requiresAuth: true } // Default for authenticated section
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('@/pages/Users.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/users/:id',
    redirect: to => `/users/${to.params.id}/todos`,
    meta: { requiresAuth: true }
  },
  {
    path: '/users/:id/todos',
    name: 'UserTodos',
    component: () => import('@/pages/UserTodos.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/todos',
    name: 'Todos',
    component: () => import('@/pages/Todos.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/posts',
    name: 'Posts',
    component: () => import('@/pages/Posts.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/albums',
    name: 'Albums',
    component: () => import('@/pages/Albums.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/feed',
    name: 'Feed',
    component: () => import('@/pages/Feed.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/pages/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/pages/Settings.vue'),
    meta: { requiresAuth: true }
  },
  // AdminDanger route is optional for local demo; gated by env flag
  ...(import.meta.env.VITE_ENABLE_ADMIN_DEMO === 'true' ? [{
    path: '/admin-danger',
    name: 'AdminDanger',
    component: () => import('@/pages/AdminDanger.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }] : []),
  {
    path: '/auth/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/auth/register',
    name: 'Register',
    component: () => import('@/pages/Register.vue'),
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const session = useSessionStore()

  // Check if route requires authentication
  if (to.meta.requiresAuth && !session.isLoggedIn) {
    next('/auth/login')
    return
  }

  // Check admin access for protected routes
  if (to.meta.requiresAdmin && !session.user?.is_superuser) {
    next('/')
    return
  }

  // If user is logged in and trying to access auth pages, redirect to home
  if (session.isLoggedIn && (to.path === '/auth/login' || to.path === '/auth/register')) {
    next('/')
    return
  }

  next()
})

export default router
