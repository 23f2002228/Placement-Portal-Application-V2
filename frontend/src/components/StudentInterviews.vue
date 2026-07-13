<template>
  <section>
    <h2>Interviews</h2>
    <button @click="loadInterviews">Refresh</button>

    <p v-if="loading">Loading interviews...</p>
    <p v-if="error" class="error">{{ error }}</p>

    <table>
      <thead>
        <tr>
          <th>Company</th>
          <th>Position</th>
          <th>Scheduled At</th>
          <th>Mode</th>
          <th>Venue / Link</th>
          <th>Round</th>
          <th>Status</th>
          <th>Feedback</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="interview in interviews" :key="interview.id">
          <td>{{ interview.company_name }}</td>
          <td>{{ interview.job_title }}</td>
          <td>{{ interview.scheduled_at }}</td>
          <td>{{ interview.mode }}</td>
          <td>{{ interview.venue_or_link || '-' }}</td>
          <td>{{ interview.round_name || '-' }}</td>
          <td>{{ interview.status }}</td>
          <td>{{ interview.feedback || '-' }}</td>
        </tr>
      </tbody>
    </table>

    <p v-if="!loading && interviews.length === 0">No interviews scheduled.</p>
  </section>
</template>

<script>
import axios from 'axios'

export default {
  name: 'StudentInterviews',
  data() {
    return {
      interviews: [],
      loading: false,
      error: '',
    }
  },
  mounted() {
    this.loadInterviews()
  },
  methods: {
    headers() {
      return {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      }
    },
    async loadInterviews() {
      this.loading = true
      this.error = ''

      try {
        const response = await axios.get('http://127.0.0.1:5000/api/student/interviews', {
          headers: this.headers(),
        })
        this.interviews = response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load interviews.'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
button { padding: 8px; border: 1px solid #bbb; background: white; cursor: pointer; margin-bottom: 12px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px; border: 1px solid #ddd; text-align: left; vertical-align: top; }
.error { color: #b42318; }
</style>
