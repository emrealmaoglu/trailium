import { createRouter, createWebHistory } from 'vue-router'
import AuthLayout from '@/layouts/AuthLayout.vue'
import AppShell from '@/layouts/AppShell.vue'

const Login = () => import('../pages/Login.vue')
const Register = () => import('../pages/Register.vue')
const Users = () => import('../pages/Users.vue')
const UserTodos = () => import('../pages/UserTodos.vue')
const Todos = () => import('../pages/Todos.vue')
const Posts = () => import('../pages/Posts.vue')
const Albums = () => import('../pages/Albums.vue')

const routes = [
  {
    path: '/auth',
    component: AuthLayout,
    children: [
      { path: 'login', name: 'login', component: Login },
      { path: 'register', name: 'register', component: Register },
    ],
  },
  {
    path: '/',
    component: AppShell,
    children: [
      { path: '', redirect: '/users' },
      { path: 'users', name: 'users', component: Users, meta: { requiresAuth: true } },
      { path: 'users/:id/todos', name: 'user-todos', component: UserTodos, meta: { requiresAuth: true } },
      { path: 'todos', name: 'todos', component: Todos, meta: { requiresAuth: true } },
      { path: 'posts', name: 'posts', component: Posts, meta: { requiresAuth: true } },
      { path: 'albums', name: 'albums', component: Albums, meta: { requiresAuth: true } },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/users' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

import { useSessionStore } from '@/stores/session'

let initTried = false
router.beforeEach(async (to, from, next) => {
  const session = useSessionStore()

  if (!initTried) {
    initTried = true
    try {
      session.loadFromStorage()
      if (session.access && !session.user) {
        await session.fetchMe().catch(() => session.logout())
      }
    } catch {}
  }

  const isAuthRoute = to.path.startsWith('/auth')
  const requiresAuth = to.matched.some(r => r.meta && r.meta.requiresAuth)

  if (isAuthRoute) {
    if (session.user) {
      const target = (to.query && to.query.redirect) || '/users'
      return next(target)
    }
    return next()
  }

  if (requiresAuth && !session.user) {
    return next({ path: '/auth/login', query: { redirect: to.fullPath } })
  }

  return next()
})

export default router
