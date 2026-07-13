<template>
  <div>
    <div v-if="!isLoggedIn">
      <StudentLogin
        v-if="showLogin"
        :message="message"
        @logged-in="handleLogin"
        @register-here="showLogin = false"
      />
      <StudentRegister
        v-else
        @registered="handleRegistered"
        @login-here="showLogin = true"
      />
    </div>

    <StudentDashboard v-else @logout="handleLogout" />
  </div>
</template>

<script>
import StudentDashboard from '@/components/StudentDashboard.vue'
import StudentLogin from '@/components/StudentLogin.vue'
import StudentRegister from '@/components/StudentRegister.vue'

export default {
  name: 'StudentView',
  components: {
    StudentDashboard,
    StudentLogin,
    StudentRegister,
  },
  data() {
    return {
      isLoggedIn:
        localStorage.getItem('access_token') &&
        localStorage.getItem('role') === 'student',
      showLogin: true,
      message: '',
    }
  },
  methods: {
    handleLogin() {
      this.isLoggedIn = true
    },
    handleRegistered() {
      this.message = 'Registration successful. Please sign in.'
      this.showLogin = true
    },
    handleLogout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('role')
      localStorage.removeItem('email')
      this.isLoggedIn = false
    },
  },
}
</script>
