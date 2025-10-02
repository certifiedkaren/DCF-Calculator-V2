import { createRouter, createWebHistory } from 'vue-router'

import DCF from '../pages/DCF.vue'
import EPS from '../pages/Earnings.vue'

const routes = [
  { path: '/', name: 'DCF', component: DCF },
  { path: '/earnings', name: 'Earnings', component: EPS },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
