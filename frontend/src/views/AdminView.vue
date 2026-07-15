<template>
  <div>
    <AdminLogin v-if="!isLoggedIn" @logged-in="handleLogin" />
    <AdminDashboard v-else @logout="handleLogout" />
  </div>
</template>

<script>
import AdminDashboard from '@/components/AdminDashboard.vue'
import AdminLogin from '@/components/AdminLogin.vue'

export default {
  name: 'AdminView',
  components: {
    AdminDashboard,
    AdminLogin,
  },
  data() {
    return {
      isLoggedIn:
        localStorage.getItem('access_token') &&
        localStorage.getItem('role') === 'admin',
    }
  },
  methods: {
    handleLogin() {
      this.isLoggedIn = true
    },
    handleLogout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('role')
      localStorage.removeItem('email')
      this.isLoggedIn = false
      this.$router.push('/')
    },
  },
}
</script>
