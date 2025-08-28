import { createRouter, createWebHistory } from 'vue-router'
import { useSessionStore } from '@/stores/session'

const routes = [
  {
    path: '/',
    redirect: '/users',
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
    name: 'UserProfileView',
    component: () => import('@/pages/UsersPage.vue'),
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
  // Connections page is not present; route removed to avoid build error
  // Feed and other features are out of scope for Sprint 0+1
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/pages/Profile.vue'),
    meta: { requiresAuth: true }
  },
  // Settings remains but not implemented in this sprint
  // AdminDanger and CookieTest are out of scope
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
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
    next('/login')
    return
  }

  // Check admin access for protected routes
  if (to.meta.requiresAdmin && !session.user?.is_superuser) {
    next('/')
    return
  }

  // If user is logged in and trying to access auth pages, redirect to home
  if (session.isLoggedIn && (to.path === '/login' || to.path === '/register')) {
    next('/')
    return
  }

  next()
})

export default router
