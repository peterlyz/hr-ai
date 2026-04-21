import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/job/:id',
    name: 'JobDetail',
    component: () => import('@/views/JobDetail.vue')
  },
  {
    path: '/talent-pool',
    name: 'TalentPool',
    component: () => import('@/views/TalentPool.vue')
  },
  {
    path: '/ai-settings',
    name: 'AISettings',
    component: () => import('@/views/AISettings.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
