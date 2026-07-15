<template>
  <div>
    <div v-if="!isLoggedIn">
      <CompanyLogin
        v-if="showLogin"
        :message="message"
        @logged-in="handleLogin"
        @register-here="showLogin = false"
      />
      <CompanyRegister
        v-else
        @registered="handleRegistered"
        @login-here="showLogin = true"
      />
    </div>

    <CompanyDashboard v-else @logout="handleLogout" />
  </div>
</template>

<script>
import CompanyDashboard from '@/components/CompanyDashboard.vue'
import CompanyLogin from '@/components/CompanyLogin.vue'
import CompanyRegister from '@/components/CompanyRegister.vue'

export default {
  name: 'CompanyView',
  components: {
    CompanyDashboard,
    CompanyLogin,
    CompanyRegister,
  },
  data() {
    return {
      isLoggedIn:
        localStorage.getItem('access_token') &&
        localStorage.getItem('role') === 'company',
      showLogin: true,
      message: '',
    }
  },
  methods: {
    handleLogin() {
      this.isLoggedIn = true
    },
    handleRegistered() {
      this.message = 'Registration successful. An admin must approve the company before login.'
      this.showLogin = true
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
