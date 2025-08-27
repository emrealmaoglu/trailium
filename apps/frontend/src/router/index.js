import { createRouter, createWebHistory } from 'vue-router'

const Users = () => import('../pages/Users.vue')
const Todos = () => import('../pages/Todos.vue')
const Posts = () => import('../pages/Posts.vue')
const Albums = () => import('../pages/Albums.vue')

const routes = [
  { path: '/', redirect: '/users' },
  { path: '/users', name: 'users', component: Users },
  { path: '/todos', name: 'todos', component: Todos },
  { path: '/posts', name: 'posts', component: Posts },
  { path: '/albums', name: 'albums', component: Albums },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
