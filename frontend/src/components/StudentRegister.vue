<template>
  <main class="auth-box">
    <form class="simple-card" @submit.prevent="register">
      <RouterLink class="home-link" to="/">Back to home</RouterLink>
      <h1>Student Register</h1>
      <p v-if="error" class="error">{{ error }}</p>

      <label>Full name<input v-model="form.full_name" required /></label>
      <label>Roll number<input v-model="form.roll_number" required /></label>
      <label>Degree<input v-model="form.degree" required /></label>
      <label>Branch<input v-model="form.branch" required /></label>
      <label>Year<input v-model.number="form.year" type="number" min="1" max="4" required /></label>
      <label>Graduation year<input v-model.number="form.graduation_year" type="number" required /></label>
      <label>CGPA<input v-model.number="form.cgpa" type="number" min="0" max="10" step="0.01" required /></label>
      <label>Phone<input v-model="form.phone" /></label>
      <!-- <label>Resume URL<input v-model="form.resume_url" /></label> -->
      <label>
        Upload resume PDF
        <input type="file" accept="application/pdf" @change="selectResume" />
      </label>
      <p class="hint">
        PDF only, up to 5 MB.
        <span v-if="resumeFileName">Selected: {{ resumeFileName }}</span>
      </p>
      <label>Skills<input v-model="form.skills" /></label>
      <label>Experience<textarea v-model="form.experience" rows="2"></textarea></label>
      <label>Email<input v-model="form.email" type="email" required /></label>
      <label>Password<input v-model="form.password" type="password" required /></label>

      <button type="submit" :disabled="isSubmitting">{{ isSubmitting ? 'Registering...' : 'Register' }}</button>
      <button type="button" @click="$emit('login-here')">Back to login</button>
    </form>
  </main>
</template>

<script>
import { RouterLink } from 'vue-router'
import axios from 'axios'

export default {
  name: 'StudentRegister',
  components: {
    RouterLink,
  },
  emits: ['registered', 'login-here'],
  data() {
    return {
      error: '',
      isSubmitting: false,
      resumeFile: null,
      resumeFileName: '',
      form: {
        full_name: '',
        roll_number: '',
        degree: '',
        branch: '',
        year: null,
        graduation_year: null,
        cgpa: null,
        phone: '',
        resume_url: '',
        skills: '',
        experience: '',
        email: '',
        password: '',
      },
    }
  },
  methods: {
    selectResume(event) {
      const file = event.target.files[0]
      this.error = ''

      if (!file) {
        this.resumeFile = null
        this.resumeFileName = ''
        return
      }

      if (file.type !== 'application/pdf') {
        this.error = 'Please upload a PDF resume.'
        event.target.value = ''
        return
      }

      if (file.size > 5 * 1024 * 1024) {
        this.error = 'Resume must be 5 MB or smaller.'
        event.target.value = ''
        return
      }

      this.resumeFile = file
      this.resumeFileName = file.name
    },
    async uploadResumeAfterRegistration() {
      if (!this.resumeFile) {
        return true
      }

      const loginResponse = await axios.post('http://127.0.0.1:5000/api/login', {
        email: this.form.email,
        password: this.form.password,
      })
      const token = loginResponse.data.data.access_token
      const formData = new FormData()
      formData.append('resume', this.resumeFile)

      await axios.post('http://127.0.0.1:5000/api/student/profile/resume', formData, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      return true
    },
    async register() {
      this.error = ''
      this.isSubmitting = true

      try {
        await axios.post('http://127.0.0.1:5000/api/register', {
          ...this.form,
          role: 'student',
        })
        try {
          await this.uploadResumeAfterRegistration()
          this.$emit('registered')
        } catch {
          this.error = 'Registration succeeded, but resume upload failed. Please sign in and upload your resume from profile.'
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Student registration failed.'
      } finally {
        this.isSubmitting = false
      }
    },
  },
}
</script>

<style scoped>
.auth-box { min-height: 100vh; display: grid; place-items: center; padding: 24px; }
.simple-card { display: grid; gap: 12px; width: min(520px, 100%); padding: 24px; border: 1px solid #ddd; background: white; }
.home-link { color: #344054; text-decoration: none; width: fit-content; }
.home-link:hover { text-decoration: underline; }
label { display: grid; gap: 6px; }
input, textarea { padding: 10px; border: 1px solid #bbb; }
button { padding: 10px 14px; cursor: pointer; }
button:disabled { cursor: wait; opacity: .7; }
.hint { margin: -6px 0 0; color: #667085; font-size: 0.9rem; }
.error { color: #b42318; }
</style>
