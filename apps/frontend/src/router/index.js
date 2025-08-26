import { createRouter, createWebHistory } from 'vue-router'

import Home   from '../pages/Home.vue'
import Todos  from '../pages/Todos.vue'
import Posts  from '../pages/Posts.vue'
import Albums from '../pages/Albums.vue'

const routes = [
  { path: '/',        name: 'home',   component: Home   },
  { path: '/todos',   name: 'todos',  component: Todos  },
  { path: '/posts',   name: 'posts',  component: Posts  },
  { path: '/albums',  name: 'albums', component: Albums },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})

import { createRouter, createWebHistory } from 'vue-router'

// Sayfalar
import UsersPage from '@/pages/UsersPage.vue'

const routes = [
  { path: '/', redirect: '/users' },          // varsayılan yönlendirme
  { path: '/users', name: 'users', component: UsersPage },

  // ileride eklenecek rotalar (şimdilik yorumda dursun)
  // { path: '/users/:id/todos', name: 'user-todos', component: () => import('@/pages/TodosPage.vue') },
  // { path: '/users/:id/posts', name: 'user-posts', component: () => import('@/pages/PostsPage.vue') },
  // { path: '/users/:id/albums', name: 'user-albums', component: () => import('@/pages/AlbumsPage.vue') },

  { path: '/:pathMatch(.*)*', name: 'not-found', component: { template: '<div class="p-6">404</div>' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
