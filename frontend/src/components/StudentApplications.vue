<template>
  <section>
    <h2>Applications</h2>

    <div class="controls">
      <select v-model="status">
        <option value="">All status</option>
        <option value="applied">Applied</option>
        <option value="shortlisted">Shortlisted</option>
        <option value="interview_scheduled">Interview scheduled</option>
        <option value="selected">Selected</option>
        <option value="rejected">Rejected</option>
        <option value="withdrawn">Withdrawn</option>
      </select>
      <button @click="loadApplications">Load applications</button>
    </div>

    <p v-if="loading">Loading applications...</p>
    <p v-if="error" class="error">{{ error }}</p>

    <table>
      <thead>
        <tr>
          <th>Company</th>
          <th>Position</th>
          <th>Status</th>
          <th>Applied On</th>
          <th>Remarks</th>
          <th>Details</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="application in applications" :key="application.id">
          <td>{{ application.company_name }}</td>
          <td>{{ application.job_title }}</td>
          <td>{{ application.status }}</td>
          <td>{{ application.application_date }}</td>
          <td>{{ application.remarks || '-' }}</td>
          <td><button @click="loadApplicationDetails(application.id)">View</button></td>
        </tr>
      </tbody>
    </table>

    <p v-if="!loading && applications.length === 0">No applications found.</p>

    <div v-if="selectedApplication" class="details">
      <h3>Application Details</h3>
      <p><b>Company:</b> {{ selectedApplication.company_name }}</p>
      <p><b>Position:</b> {{ selectedApplication.job_title }}</p>
      <p><b>Status:</b> {{ selectedApplication.status }}</p>
      <p><b>Remarks:</b> {{ selectedApplication.remarks || '-' }}</p>

      <h4>Status History</h4>
      <ul>
        <li v-for="history in selectedApplication.status_history" :key="history.id">
          {{ history.changed_at }}: {{ history.old_status || 'new' }} to {{ history.new_status }}
          <span v-if="history.note">- {{ history.note }}</span>
        </li>
      </ul>
      <p v-if="selectedApplication.status_history.length === 0">No status history found.</p>
    </div>
  </section>
</template>

<script>
import axios from 'axios'

export default {
  name: 'StudentApplications',
  data() {
    return {
      applications: [],
      selectedApplication: null,
      status: '',
      loading: false,
      error: '',
    }
  },
  mounted() {
    this.loadApplications()
  },
  methods: {
    headers() {
      return {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      }
    },
    async loadApplications() {
      this.loading = true
      this.error = ''

      try {
        const response = await axios.get('http://127.0.0.1:5000/api/student/applications', {
          params: {
            status: this.status,
          },
          headers: this.headers(),
        })
        this.applications = response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load applications.'
      } finally {
        this.loading = false
      }
    },
    async loadApplicationDetails(applicationId) {
      this.error = ''

      try {
        const response = await axios.get(
          `http://127.0.0.1:5000/api/student/applications/${applicationId}`,
          { headers: this.headers() },
        )
        this.selectedApplication = response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load application details.'
      }
    },
  },
}
</script>

<style scoped>
.controls { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
select, button { padding: 8px; border: 1px solid #bbb; }
button { cursor: pointer; background: white; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px; border: 1px solid #ddd; text-align: left; vertical-align: top; }
.details { margin-top: 18px; border: 1px solid #ddd; padding: 14px; }
.details p { margin: 0 0 6px; }
.error { color: #b42318; }
</style>
