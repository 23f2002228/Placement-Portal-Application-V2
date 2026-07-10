<template>
  <section>
    <h2>Overview</h2>
    <p v-if="loading">Loading dashboard...</p>
    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="dashboard" class="stats">
      <div><b>{{ dashboard.total_students }}</b><span>Total students</span></div>
      <div><b>{{ dashboard.total_companies }}</b><span>Total companies</span></div>
      <div><b>{{ dashboard.pending_companies }}</b><span>Pending companies</span></div>
      <div><b>{{ dashboard.approved_companies }}</b><span>Approved companies</span></div>
      <div><b>{{ dashboard.active_approved_companies }}</b><span>Active approved companies</span></div>
      <div><b>{{ dashboard.blacklisted_companies }}</b><span>Blacklisted companies</span></div>
      <div><b>{{ dashboard.total_drives }}</b><span>Total drives</span></div>
      <div><b>{{ dashboard.pending_drives }}</b><span>Pending drives</span></div>
      <div><b>{{ dashboard.total_applications }}</b><span>Total applications</span></div>
      <div><b>{{ dashboard.blacklisted_users }}</b><span>Blacklisted users</span></div>
    </div>
  </section>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AdminOverview',
  data() {
    return {
      dashboard: null,
      loading: false,
      error: '',
    }
  },
  mounted() {
    this.loadDashboard()
  },
  methods: {
    async loadDashboard() {
      this.loading = true
      this.error = ''

      try {
        const response = await axios.get('http://127.0.0.1:5000/api/admin/dashboard', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        })
        this.dashboard = response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load dashboard.'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.stats { display: grid; grid-template-columns: repeat(4, minmax(140px, 1fr)); gap: 12px; }
.stats div { border: 1px solid #ddd; padding: 14px; }
.stats b, .stats span { display: block; }
.stats b { font-size: 1.6rem; }
.stats span { color: #667085; }
.error { color: #b42318; }
@media (max-width: 700px) { .stats { grid-template-columns: 1fr 1fr; } }
</style>
