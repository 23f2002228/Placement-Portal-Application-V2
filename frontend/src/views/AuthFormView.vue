<script setup>
import axios from 'axios'
import { computed, reactive, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

const props = defineProps({ role: String, mode: String })
const route = useRoute()
const router = useRouter()
const roleName = computed(() => props.role.charAt(0).toUpperCase() + props.role.slice(1))
const form = reactive({
  email: '',
  password: '',
  full_name: '',
  roll_number: '',
  degree: '',
  branch: '',
  year: null,
  graduation_year: null,
  cgpa: null,
  phone: '',
  skills: '',
  company_name: '',
  industry: '',
  location: '',
  hr_name: '',
  hr_contact: '',
  website: '',
  description: '',
})
const errorMessage = ref('')
const successMessage = computed(() =>
  route.query.registered ? 'Registration successful. You can now sign in.' : '',
)
const isSubmitting = ref(false)

async function submitForm() {
  errorMessage.value = ''

  isSubmitting.value = true

  try {
    if (props.mode === 'register') {
      await axios.post('http://127.0.0.1:5000/api/register', {
        ...form,
        role: props.role,
      })
      await router.push({ path: `/${props.role}/login`, query: { registered: '1' } })
      return
    }

    const endpoint = props.role === 'admin' ? '/api/admin/login' : '/api/login'
    const response = await axios.post(`http://127.0.0.1:5000${endpoint}`, {
      email: form.email,
      password: form.password,
    })
    const authData = response.data.data

    localStorage.setItem('access_token', authData.access_token)
    localStorage.setItem('role', authData.role)
    localStorage.setItem('email', authData.email)

    await router.push(`/${authData.role}`)
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Unable to connect to the server.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <form class="auth-form card" @submit.prevent="submitForm">
      <RouterLink class="auth-form__back" :to="`/${mode}`">← Back</RouterLink>
      <span>{{ roleName }} portal</span>
      <h1>{{ mode === 'login' ? 'Sign in' : 'Create account' }}</h1>
      <p>{{ mode === 'login' ? `Welcome back to the ${roleName.toLowerCase()} portal.` : `Register as a ${roleName.toLowerCase()}.` }}</p>
      <template v-if="mode === 'register' && role === 'student'">
        <label>Full name<input v-model.trim="form.full_name" type="text" required /></label>
        <label>Roll number<input v-model.trim="form.roll_number" type="text" required /></label>
        <label>Degree<input v-model.trim="form.degree" type="text" required /></label>
        <label>Branch<input v-model.trim="form.branch" type="text" required /></label>
        <label>Current year<input v-model.number="form.year" type="number" min="1" max="4" required /></label>
        <label>Graduation year<input v-model.number="form.graduation_year" type="number" min="2020" required /></label>
        <label>CGPA<input v-model.number="form.cgpa" type="number" min="0" max="10" step="0.01" required /></label>
        <label>Phone <small>(optional)</small><input v-model.trim="form.phone" type="tel" /></label>
        <label>Skills <small>(optional)</small><input v-model.trim="form.skills" type="text" /></label>
      </template>
      <template v-if="mode === 'register' && role === 'company'">
        <label>Company name<input v-model.trim="form.company_name" type="text" required /></label>
        <label>Industry<input v-model.trim="form.industry" type="text" required /></label>
        <label>Location<input v-model.trim="form.location" type="text" required /></label>
        <label>HR name<input v-model.trim="form.hr_name" type="text" required /></label>
        <label>HR contact<input v-model.trim="form.hr_contact" type="text" required /></label>
        <label>Website <small>(optional)</small><input v-model.trim="form.website" type="url" /></label>
        <label>Description <small>(optional)</small><textarea v-model.trim="form.description" rows="3"></textarea></label>
      </template>
      <label>Email<input v-model.trim="form.email" type="email" placeholder="you@example.com" required /></label>
      <label>Password<input v-model="form.password" type="password" placeholder="Enter your password" required /></label>
      <p v-if="successMessage" class="auth-form__success">{{ successMessage }}</p>
      <p v-if="errorMessage" class="auth-form__error">{{ errorMessage }}</p>
      <button class="button" type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Register' }}
      </button>
      <small v-if="mode === 'login'">Your session is protected with a JWT access token.</small>
      <small v-else-if="role === 'company'">An admin must approve the company before it can sign in.</small>
    </form>
  </main>
</template>

<style scoped>
.auth-page { display: grid; min-height: 100vh; place-items: center; padding: 30px; background: #f6f8fc; }.auth-form { display: grid; width: min(430px, 100%); gap: 18px; padding: 34px; }
.auth-form__back { color: var(--text-muted); font-size: .85rem; font-weight: 700; }.auth-form > span { color: var(--blue); font-size: .72rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.auth-form h1 { margin: -8px 0 0; font-size: 2rem; }.auth-form p,.auth-form small { margin: -10px 0 0; color: var(--text-muted); }.auth-form label { display: grid; gap: 7px; font-size: .82rem; font-weight: 700; }
.auth-form input,.auth-form textarea { width: 100%; padding: 0 12px; border: 1px solid #d0d5dd; border-radius: 9px; background: white; }.auth-form input { height: 44px; }.auth-form textarea { padding-block: 10px; resize: vertical; }
.auth-form .auth-form__error { margin: 0; color: #b42318; font-size: .82rem; font-weight: 650; }
.auth-form .auth-form__success { margin: 0; color: #067647; font-size: .82rem; font-weight: 650; }
.auth-form button:disabled { cursor: wait; opacity: .7; }
</style>
