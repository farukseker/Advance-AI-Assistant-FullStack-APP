import { createRouter, createWebHistory } from 'vue-router'
import BaseView from '../views/BaseView.vue'
import DefaultLayout from '../layouts/default.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: DefaultLayout,
      meta: { title: 'Chat' },
      children: [
        {
          path: '',
          name: 'home',
          component: BaseView
        },
        {
          path:'/export',
          name: 'export',
          component: () => import('../views/ExportIdea.vue')
        }
      ]
    },
  ]
})

export default router
