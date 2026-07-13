<template>
  <section>
    <h2>Student Profile</h2>
    <p v-if="loading">Loading profile...</p>
    <p v-if="message" class="success">{{ message }}</p>
    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="!isEditing" class="profile-view">
      <p><b>Name:</b> {{ form.full_name }}</p>
      <p><b>Email:</b> {{ form.email }}</p>
      <p><b>Roll number:</b> {{ form.roll_number }}</p>
      <p><b>Degree:</b> {{ form.degree }}</p>
      <p><b>Branch:</b> {{ form.branch }}</p>
      <p><b>Year:</b> {{ form.year }}</p>
      <p><b>Graduation year:</b> {{ form.graduation_year }}</p>
      <p><b>CGPA:</b> {{ form.cgpa }}</p>
      <p><b>Phone:</b> {{ form.phone || '-' }}</p>
      <p><b>Resume:</b> <a v-if="form.resume_url" :href="form.resume_url" target="_blank">Open resume</a><span v-else>-</span></p>
      <p><b>Skills:</b> {{ form.skills || '-' }}</p>
      <p><b>Experience:</b> {{ form.experience || '-' }}</p>

      <button @click="isEditing = true">Edit profile</button>
    </div>

    <form v-else class="form-grid" @submit.prevent="saveProfile">
      <label>Full name<input v-model="form.full_name" required /></label>
      <label>Roll number<input v-model="form.roll_number" required /></label>
      <label>Degree<input v-model="form.degree" required /></label>
      <label>Branch<input v-model="form.branch" required /></label>
      <label>Year<input v-model.number="form.year" type="number" min="1" max="4" required /></label>
      <label>Graduation year<input v-model.number="form.graduation_year" type="number" required /></label>
      <label>CGPA<input v-model.number="form.cgpa" type="number" min="0" max="10" step="0.01" required /></label>
      <label>Phone<input v-model="form.phone" /></label>
      <label class="wide">Resume URL<input v-model="form.resume_url" /></label>
      <label class="wide">Skills<textarea v-model="form.skills" rows="2"></textarea></label>
      <label class="wide">Experience<textarea v-model="form.experience" rows="3"></textarea></label>

      <div class="form-actions">
        <button type="submit">Save profile</button>
        <button type="button" @click="cancelEdit">Cancel</button>
      </div>
    </form>
  </section>
</template>

<script>
import axios from 'axios'

export default {
  name: 'StudentProfile',
  data() {
    return {
      form: this.emptyForm(),
      isEditing: false,
      loading: false,
      error: '',
      message: '',
    }
  },
  mounted() {
    this.loadProfile()
  },
  methods: {
    emptyForm() {
      return {
        email: '',
        full_name: '',
        roll_number: '',
        degree: '',
        branch: '',
        year: '',
        graduation_year: '',
        cgpa: '',
        phone: '',
        resume_url: '',
        skills: '',
        experience: '',
      }
    },
    headers() {
      return {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      }
    },
    async loadProfile() {
      this.loading = true
      this.error = ''

      try {
        const response = await axios.get('http://127.0.0.1:5000/api/student/profile', {
          headers: this.headers(),
        })
        this.form = {
          email: response.data.email || '',
          full_name: response.data.full_name || '',
          roll_number: response.data.roll_number || '',
          degree: response.data.degree || '',
          branch: response.data.branch || '',
          year: response.data.year || '',
          graduation_year: response.data.graduation_year || '',
          cgpa: response.data.cgpa || '',
          phone: response.data.phone || '',
          resume_url: response.data.resume_url || '',
          skills: response.data.skills || '',
          experience: response.data.experience || '',
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load student profile.'
      } finally {
        this.loading = false
      }
    },
    async saveProfile() {
      this.error = ''
      this.message = ''

      try {
        await axios.patch('http://127.0.0.1:5000/api/student/profile', this.form, {
          headers: this.headers(),
        })
        this.message = 'Profile updated successfully.'
        this.isEditing = false
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not update student profile.'
      }
    },
    cancelEdit() {
      this.isEditing = false
      this.loadProfile()
    },
  },
}
</script>

<style scoped>
.profile-view { display: grid; gap: 6px; max-width: 760px; }
.profile-view p { margin: 0; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(220px, 1fr)); gap: 12px; max-width: 900px; }
label { display: grid; gap: 6px; }
.wide, .form-actions { grid-column: 1 / -1; }
input, textarea, button { padding: 8px; border: 1px solid #bbb; }
button { width: fit-content; cursor: pointer; background: white; }
.form-actions { display: flex; flex-wrap: wrap; gap: 8px; }
.error { color: #b42318; }
.success { color: #067647; }
@media (max-width: 700px) { .form-grid { grid-template-columns: 1fr; } }
</style>
