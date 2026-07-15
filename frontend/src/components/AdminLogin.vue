<template>
  <main class="auth-box">
    <form class="simple-card" @submit.prevent="login">
      <RouterLink class="home-link" to="/">Back to home</RouterLink>
      <h1>Admin Login</h1>
      <p v-if="error" class="error">{{ error }}</p>

      <label>
        Email
        <input v-model="email" type="email" required />
      </label>

      <label>
        Password
        <input v-model="password" type="password" required />
      </label>

      <button type="submit">Login</button>
    </form>
  </main>
</template>

<script>
import { RouterLink } from 'vue-router'
import axios from 'axios'

export default {
  name: 'AdminLogin',
  components: {
    RouterLink,
  },
  emits: ['logged-in'],
  data() {
    return {
      email: '',
      password: '',
      error: '',
    }
  },
  methods: {
    async login() {
      this.error = ''

      try {
        const response = await axios.post('http://127.0.0.1:5000/api/admin/login', {
          email: this.email,
          password: this.password,
        })
        const data = response.data.data

        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('role', data.role)
        localStorage.setItem('email', data.email)

        this.$emit('logged-in')
      } catch (error) {
        this.error = error.response?.data?.message || 'Admin login failed.'
      }
    },
  },
}
</script>
