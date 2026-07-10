<template>
  <section>
    <h2>Applications</h2>

    <div class="controls">
      <input v-model="search" placeholder="Search student, company, job" />
      <select v-model="status">
        <option value="">All status</option>
        <option value="applied">Applied</option>
        <option value="shortlisted">Shortlisted</option>
        <option value="interview_scheduled">Interview scheduled</option>
        <option value="selected">Selected</option>
        <option value="rejected">Rejected</option>
        <option value="withdrawn">Withdrawn</option>
      </select>
      <button @click="loadApplications">Search</button>
    </div>

    <p v-if="loading">Loading applications...</p>
    <p v-if="error" class="error">{{ error }}</p>

    <table>
      <thead>
        <tr>
          <th>Student</th>
          <th>Roll No.</th>
          <th>Company</th>
          <th>Job Title</th>
          <th>Status</th>
          <th>Date</th>
          <th>Remarks</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="application in applications" :key="application.id">
          <td>{{ application.student_name }}</td>
          <td>{{ application.student_roll_number }}</td>
          <td>{{ application.company_name }}</td>
          <td>{{ application.job_title }}</td>
          <td>{{ application.status }}</td>
          <td>{{ application.application_date }}</td>
          <td>{{ application.remarks }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AdminApplications',
  data() {
    return {
      applications: [],
      search: '',
      status: '',
      loading: false,
      error: '',
    }
  },
  mounted() {
    this.loadApplications()
  },
  methods: {
    async loadApplications() {
      this.loading = true
      this.error = ''

      try {
        const response = await axios.get('http://127.0.0.1:5000/api/admin/applications', {
          params: {
            search: this.search,
            status: this.status,
          },
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        })
        this.applications = response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load applications.'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.controls { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }
input, select, button { padding: 8px; border: 1px solid #bbb; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px; border: 1px solid #ddd; text-align: left; }
.error { color: #b42318; }
</style>
