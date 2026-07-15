<template>
  <section>
    <h2>Company Profile</h2>
    <p v-if="loading">Loading profile...</p>
    <p v-if="message" class="success">{{ message }}</p>
    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="!isEditing" class="profile-view">
      <p><b>Company name:</b> {{ form.company_name }}</p>
      <p><b>Industry:</b> {{ form.industry }}</p>
      <p><b>Location:</b> {{ form.location }}</p>
      <p><b>HR name:</b> {{ form.hr_name }}</p>
      <p><b>HR contact:</b> {{ form.hr_contact }}</p>
      <p><b>Website:</b> {{ form.website || '-' }}</p>
      <p><b>Description:</b> {{ form.description || '-' }}</p>

      <button @click="isEditing = true">Edit profile</button>
    </div>

    <form v-else class="form-grid" @submit.prevent="saveProfile">
      <label>Company name<input v-model="form.company_name" required /></label>
      <label>Industry<input v-model="form.industry" required /></label>
      <label>Location<input v-model="form.location" required /></label>
      <label>HR name<input v-model="form.hr_name" required /></label>
      <label>HR contact<input v-model="form.hr_contact" required /></label>
      <label>Website<input v-model="form.website" /></label>
      <label class="wide">Description<textarea v-model="form.description" rows="3"></textarea></label>

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
  name: 'CompanyProfile',
  data() {
    return {
      form: {
        company_name: '',
        industry: '',
        location: '',
        hr_name: '',
        hr_contact: '',
        website: '',
        description: '',
      },
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
    headers() {
      return {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      }
    },
    async loadProfile() {
      this.loading = true
      this.error = ''

      try {
        const response = await axios.get('http://127.0.0.1:5000/api/company/profile', {
          headers: this.headers(),
        })
        this.form = {
          company_name: response.data.company_name || '',
          industry: response.data.industry || '',
          location: response.data.location || '',
          hr_name: response.data.hr_name || '',
          hr_contact: response.data.hr_contact || '',
          website: response.data.website || '',
          description: response.data.description || '',
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load company profile.'
      } finally {
        this.loading = false
      }
    },
    async saveProfile() {
      this.error = ''
      this.message = ''

      try {
        await axios.patch('http://127.0.0.1:5000/api/company/profile', this.form, {
          headers: this.headers(),
        })
        this.message = 'Profile updated successfully.'
        this.isEditing = false
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not update company profile.'
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
.profile-view { display: grid; gap: 6px; max-width: 700px; }
.profile-view p { margin: 0; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(220px, 1fr)); gap: 12px; max-width: 900px; }
label { display: grid; gap: 6px; }
.wide, .form-actions { grid-column: 1 / -1; }
input, textarea { padding: 8px; border: 1px solid #bbb; }
button { width: fit-content; }
.form-actions { display: flex; flex-wrap: wrap; gap: 8px; }
.error { color: #b42318; }
.success { color: #067647; }
@media (max-width: 700px) { .form-grid { grid-template-columns: 1fr; } }
</style>
