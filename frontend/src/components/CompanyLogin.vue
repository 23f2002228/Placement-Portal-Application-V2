<template>
  <main class="auth-box">
    <form class="simple-card" @submit.prevent="login">
      <RouterLink class="home-link" to="/">Back to home</RouterLink>
      <h1>Company Login</h1>
      <p v-if="message" class="success">{{ message }}</p>
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
      <button type="button" @click="$emit('register-here')">Register company</button>
    </form>
  </main>
</template>

<script>
import { RouterLink } from 'vue-router'
import axios from 'axios'

export default {
  name: 'CompanyLogin',
  components: {
    RouterLink,
  },
  props: {
    message: {
      type: String,
      default: '',
    },
  },
  emits: ['logged-in', 'register-here'],
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
        const response = await axios.post('http://127.0.0.1:5000/api/login', {
          email: this.email,
          password: this.password,
        })
        const data = response.data.data

        if (data.role !== 'company') {
          this.error = 'Please use the correct company account.'
          return
        }

        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('role', data.role)
        localStorage.setItem('email', data.email)

        this.$emit('logged-in')
      } catch (error) {
        const approvalStatus = error.response?.data?.approval_status

        if (approvalStatus === 'pending') {
          this.error = 'Your company registration is waiting for admin approval.'
          return
        }

        if (approvalStatus === 'rejected') {
          this.error = 'Your company registration was rejected. Please contact the placement admin.'
          return
        }

        this.error = error.response?.data?.message || 'Company login failed.'
      }
    },
  },
}
</script>
