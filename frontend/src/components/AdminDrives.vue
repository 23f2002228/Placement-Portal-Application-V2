<template>
  <section>
    <h2>Placement Drives</h2>

    <div class="controls">
      <input v-model="search" placeholder="Search job, company, skills" @keyup.enter="loadDrives" />
      <select v-model="status">
        <option value="">All status</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
        <option value="closed">Closed</option>
      </select>
      <button @click="loadDrives">Search</button>
    </div>

    <p v-if="loading">Loading drives...</p>
    <p v-if="error" class="error">{{ error }}</p>

    <table>
      <thead>
        <tr>
          <th>Job Title</th>
          <th>Company</th>
          <th>Location</th>
          <th>Salary</th>
          <th>Min CGPA</th>
          <th>Year</th>
          <th>Status</th>
          <th>Applications</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="drive in drives" :key="drive.id">
          <td>{{ drive.job_title }}</td>
          <td>{{ drive.company_name }}</td>
          <td>{{ drive.location }}</td>
          <td>{{ drive.salary }}</td>
          <td>{{ drive.min_cgpa }}</td>
          <td>{{ drive.eligible_year }}</td>
          <td>{{ drive.status }}</td>
          <td>{{ drive.applications_count }}</td>
          <td class="actions">
            <button @click="approveDrive(drive.id)">Approve</button>
            <button @click="rejectDrive(drive.id)">Reject</button>
            <button @click="closeDrive(drive.id)">Close</button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AdminDrives',
  emits: ['dashboard-changed'],
  data() {
    return {
      drives: [],
      search: '',
      status: '',
      loading: false,
      error: '',
    }
  },
  mounted() {
    this.loadDrives()
  },
  methods: {
    headers() {
      return {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      }
    },
    async loadDrives() {
      this.loading = true
      this.error = ''

      try {
        const response = await axios.get('http://127.0.0.1:5000/api/admin/drives', {
          params: {
            search: this.search,
            status: this.status,
          },
          headers: this.headers(),
        })
        this.drives = response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load drives.'
      } finally {
        this.loading = false
      }
    },
    async approveDrive(id) {
      this.error = ''

      try {
        await axios.patch(`http://127.0.0.1:5000/api/admin/drives/${id}/approve`, {}, {
          headers: this.headers(),
        })
        this.$emit('dashboard-changed')
        this.loadDrives()
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not approve drive.'
      }
    },
    async rejectDrive(id) {
      const reason = window.prompt('Reason for rejection?', '')

      if (reason === null) return

      this.error = ''

      try {
        await axios.patch(`http://127.0.0.1:5000/api/admin/drives/${id}/reject`, { reason }, {
          headers: this.headers(),
        })
        this.$emit('dashboard-changed')
        this.loadDrives()
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not reject drive.'
      }
    },
    async closeDrive(id) {
      this.error = ''

      try {
        await axios.patch(`http://127.0.0.1:5000/api/admin/drives/${id}/close`, {}, {
          headers: this.headers(),
        })
        this.$emit('dashboard-changed')
        this.loadDrives()
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not close drive.'
      }
    },
  },
}
</script>

<style scoped>
.controls { margin: 12px 0; }
</style>
