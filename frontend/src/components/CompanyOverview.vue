<template>
  <section>
    <h2>Overview</h2>
    <p v-if="loading">Loading dashboard...</p>
    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="dashboard" class="stats">
      <div><b>{{ dashboard.total_jobs }}</b><span>Total jobs</span></div>
      <div><b>{{ dashboard.active_jobs }}</b><span>Active jobs</span></div>
      <div><b>{{ dashboard.pending_jobs }}</b><span>Pending jobs</span></div>
      <div><b>{{ dashboard.closed_jobs }}</b><span>Closed jobs</span></div>
      <div><b>{{ dashboard.received_applications }}</b><span>Applications</span></div>
      <div><b>{{ dashboard.shortlisted_candidates }}</b><span>Shortlisted</span></div>
      <div><b>{{ dashboard.selected_candidates }}</b><span>Selected</span></div>
    </div>
  </section>
</template>

<script>
import axios from 'axios'

export default {
  name: 'CompanyOverview',
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
    headers() {
      return {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      }
    },
    async loadDashboard() {
      this.loading = true
      this.error = ''

      try {
        const response = await axios.get('http://127.0.0.1:5000/api/company/dashboard', {
          headers: this.headers(),
        })
        this.dashboard = response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load company dashboard.'
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
