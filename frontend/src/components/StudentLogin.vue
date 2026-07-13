<template>
  <main class="auth-box">
    <form class="simple-card" @submit.prevent="login">
      <RouterLink class="home-link" to="/">Back to home</RouterLink>
      <h1>Student Login</h1>
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
      <button type="button" @click="$emit('register-here')">Register as student</button>
    </form>
  </main>
</template>

<script>
import { RouterLink } from 'vue-router'
import axios from 'axios'

export default {
  name: 'StudentLogin',
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

        if (data.role !== 'student') {
          this.error = 'Please use the correct student account.'
          return
        }

        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('role', data.role)
        localStorage.setItem('email', data.email)

        this.$emit('logged-in')
      } catch (error) {
        this.error = error.response?.data?.message || 'Student login failed.'
      }
    },
  },
}
</script>

<style scoped>
.auth-box { min-height: 100vh; display: grid; place-items: center; padding: 24px; }
.simple-card { display: grid; gap: 14px; width: min(420px, 100%); padding: 24px; border: 1px solid #ddd; background: white; }
.home-link { color: #344054; text-decoration: none; width: fit-content; }
.home-link:hover { text-decoration: underline; }
label { display: grid; gap: 6px; }
input { padding: 10px; border: 1px solid #bbb; }
button { padding: 10px 14px; cursor: pointer; }
.error { color: #b42318; }
.success { color: #067647; }
</style>
