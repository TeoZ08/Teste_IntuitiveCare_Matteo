import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import OperadorasView from '../views/OperadorasView.vue'
import OperadoraDetalheView from '../views/OperadoraDetalheView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'dashboard', component: DashboardView },
    { path: '/operadoras', name: 'operadoras', component: OperadorasView },
    { path: '/operadoras/:id', name: 'detalhe', component: OperadoraDetalheView }
  ]
})

export default router