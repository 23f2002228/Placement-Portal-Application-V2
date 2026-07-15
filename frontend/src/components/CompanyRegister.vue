<template>
  <main class="auth-box">
    <form class="simple-card" @submit.prevent="register">
      <RouterLink class="home-link" to="/">Back to home</RouterLink>
      <h1>Company Register</h1>
      <p v-if="error" class="error">{{ error }}</p>

      <label>Company name<input v-model="form.company_name" required /></label>
      <label>Industry<input v-model="form.industry" required /></label>
      <label>Location<input v-model="form.location" required /></label>
      <label>HR name<input v-model="form.hr_name" required /></label>
      <label>HR contact<input v-model="form.hr_contact" required /></label>
      <label>Website<input v-model="form.website" /></label>
      <label>Description<textarea v-model="form.description" rows="3"></textarea></label>
      <label>Email<input v-model="form.email" type="email" required /></label>
      <label>Password<input v-model="form.password" type="password" required /></label>

      <button type="submit">Register</button>
      <button type="button" @click="$emit('login-here')">Back to login</button>
    </form>
  </main>
</template>

<script>
import { RouterLink } from 'vue-router'
import axios from 'axios'

export default {
  name: 'CompanyRegister',
  components: {
    RouterLink,
  },
  emits: ['registered', 'login-here'],
  data() {
    return {
      error: '',
      form: {
        company_name: '',
        industry: '',
        location: '',
        hr_name: '',
        hr_contact: '',
        website: '',
        description: '',
        email: '',
        password: '',
      },
    }
  },
  methods: {
    async register() {
      this.error = ''

      try {
        await axios.post('http://127.0.0.1:5000/api/register', {
          ...this.form,
          role: 'company',
        })
        this.$emit('registered')
      } catch (error) {
        this.error = error.response?.data?.message || 'Company registration failed.'
      }
    },
  },
}
</script>
