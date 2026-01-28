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
          path:'/settings',
          name: 'settings',
          component: () => import('../views/SettingsView.vue'),
          props: true
        },
        {
          path:'/audio-create',
          name: 'audio-create',
          component: () => import('../views/AudioCreateView.vue'),
          props: true
        },
        {
          path:'/chat/:chat_id',
          name: 'chat',
          component: () => import('../views/ChatView.vue'),
          props: true
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

router.beforeEach((to, from, next) => {
  const audios = document.querySelectorAll('audio')

  audios.forEach(audio => {
    try {
      audio.pause()
      audio.currentTime = 0
      audio.src = ''        // important: buffer reset
      audio.load()
    } catch (_) {}
  })

  next()
})

export default router
