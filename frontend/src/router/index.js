import { createRouter, createWebHistory } from 'vue-router'
import Datasets from '../views/Datasets.vue'
import ChorusModels from '../views/ChorusModels.vue'
import Bots from '../views/Bots.vue'
import Chat from '../views/Chat.vue'

const routes = [
  {
    path: '/',
    redirect: '/datasets'
  },
  {
    path: '/datasets',
    name: 'Datasets',
    component: Datasets
  },
  {
    path: '/chorus-models',
    name: 'ChorusModels',
    component: ChorusModels
  },
  {
    path: '/bots',
    name: 'Bots',
    component: Bots
  },
  {
    path: '/chat/:botId',
    name: 'Chat',
    component: Chat
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

