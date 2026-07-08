import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '../views/LandingView.vue'
import LoginView from '../views/LoginView.vue'
import AuthFormView from '../views/AuthFormView.vue'
import StudentDashboardView from '../views/StudentDashboardView.vue'
import CompanyDashboardView from '../views/CompanyDashboardView.vue'
import AdminDashboardView from '../views/AdminDashboardView.vue'
import WorkspacePlaceholderView from '../views/WorkspacePlaceholderView.vue'
import StudentProfileView from '../views/StudentProfileView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: LandingView,
    },
    { path: '/login', name: 'login', component: LoginView, props: { mode: 'login' } },
    { path: '/register', name: 'register', component: LoginView, props: { mode: 'register' } },
    { path: '/student/login', component: AuthFormView, props: { role: 'student', mode: 'login' } },
    { path: '/student/register', component: AuthFormView, props: { role: 'student', mode: 'register' } },
    { path: '/company/login', component: AuthFormView, props: { role: 'company', mode: 'login' } },
    { path: '/company/register', component: AuthFormView, props: { role: 'company', mode: 'register' } },
    { path: '/admin/login', component: AuthFormView, props: { role: 'admin', mode: 'login' } },
    { path: '/student', name: 'student-dashboard', component: StudentDashboardView, meta: { requiresAuth: true, role: 'student' } },
    { path: '/company', name: 'company-dashboard', component: CompanyDashboardView, meta: { requiresAuth: true, role: 'company' } },
    { path: '/admin', name: 'admin-dashboard', component: AdminDashboardView, meta: { requiresAuth: true, role: 'admin' } },
    { path: '/student/drives', component: WorkspacePlaceholderView, meta: { requiresAuth: true, role: 'student', title: 'Placement drives' } },
    { path: '/student/applications', component: WorkspacePlaceholderView, meta: { requiresAuth: true, role: 'student', title: 'My applications' } },
    {
      path: '/student/profile',
      component: StudentProfileView,
      meta: { requiresAuth: true, role: 'student' },
    },
    { path: '/company/drives', component: WorkspacePlaceholderView, meta: { requiresAuth: true, role: 'company', title: 'Placement drives' } },
    { path: '/company/applicants', component: WorkspacePlaceholderView, meta: { requiresAuth: true, role: 'company', title: 'Applicants' } },
    { path: '/company/profile', component: WorkspacePlaceholderView, meta: { requiresAuth: true, role: 'company', title: 'Company profile' } },
    { path: '/admin/companies', component: WorkspacePlaceholderView, meta: { requiresAuth: true, role: 'admin', title: 'Company management' } },
    { path: '/admin/students', component: WorkspacePlaceholderView, meta: { requiresAuth: true, role: 'admin', title: 'Student management' } },
    { path: '/admin/drives', component: WorkspacePlaceholderView, meta: { requiresAuth: true, role: 'admin', title: 'Drive approvals' } },
    { path: '/admin/reports', component: WorkspacePlaceholderView, meta: { requiresAuth: true, role: 'admin', title: 'Reports' } },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach((to) => {
  if (!to.meta.requiresAuth) return true

  const accessToken = localStorage.getItem('access_token')
  const role = localStorage.getItem('role')

  if (!accessToken || !role) {
    return `/${to.meta.role}/login`
  }

  if (role !== to.meta.role) {
    return ['student', 'company', 'admin'].includes(role) ? `/${role}` : '/login'
  }

  return true
})

export default router
