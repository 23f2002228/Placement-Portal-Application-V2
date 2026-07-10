import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '../views/LandingView.vue'
import AdminView from '../views/AdminView.vue'
import StudentView from '../views/StudentView.vue'
import CompanyView from '../views/CompanyView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: LandingView,
    },
    { path: '/admin', name: 'admin', component: AdminView },
    { path: '/student', name: 'student', component: StudentView },
    { path: '/company', name: 'company', component: CompanyView },
    { path: '/login', redirect: '/' },
    { path: '/register', redirect: '/' },
    { path: '/admin/login', redirect: '/admin' },
    { path: '/student/login', redirect: '/student' },
    { path: '/student/register', redirect: '/student' },
    { path: '/company/login', redirect: '/company' },
    { path: '/company/register', redirect: '/company' },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

export default router
