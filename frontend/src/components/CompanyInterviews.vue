<template>
  <section>
    <h2>Interviews</h2>

    <p v-if="loading">Loading interviews...</p>
    <p v-if="error" class="error">{{ error }}</p>

    <table>
      <thead>
        <tr>
          <th>Candidate</th>
          <th>Job</th>
          <th>Scheduled At</th>
          <th>Mode</th>
          <th>Venue / Link</th>
          <th>Round</th>
          <th>Interview Status</th>
          <th>Application</th>
          <th>Feedback</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="interview in interviews" :key="interview.id">
          <td>
            <b>{{ interview.student_name || 'Student' }}</b><br />
            {{ interview.student_email || '-' }}
          </td>
          <td>
            {{ interview.job_title || '-' }}<br />
            <span class="muted">Application #{{ interview.application_id }}</span>
          </td>
          <td>{{ formatDate(interview.scheduled_at) }}</td>
          <td>{{ statusLabel(interview.mode) }}</td>
          <td>{{ interview.venue_or_link || '-' }}</td>
          <td>{{ interview.round_name || '-' }}</td>
          <td>
            <span class="badge" :class="interview.status">
              {{ statusLabel(interview.status) }}
            </span>
          </td>
          <td>{{ applicationStatusLabel(interview.application_status) }}</td>
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
  name: 'CompanyInterviews',
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
        const response = await axios.get('http://127.0.0.1:5000/api/company/interviews', {
          headers: this.headers(),
        })
        this.interviews = response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load interviews.'
      } finally {
        this.loading = false
      }
    },
    formatDate(value) {
      if (!value) return '-'
      return new Date(value).toLocaleString()
    },
    statusLabel(status) {
      if (!status) return '-'

      const labels = {
        online: 'Online',
        offline: 'Offline',
        scheduled: 'Scheduled',
        completed: 'Completed',
        cancelled: 'Cancelled',
      }

      return labels[status] || status
    },
    applicationStatusLabel(status) {
      if (!status) return '-'

      const labels = {
        applied: 'Applied',
        shortlisted: 'Shortlisted',
        interview_scheduled: 'Interview',
        selected: 'Selected',
        rejected: 'Rejected',
        withdrawn: 'Withdrawn',
      }

      return labels[status] || status
    },
  },
}
</script>

<style scoped>
table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px; border: 1px solid #ddd; text-align: left; vertical-align: top; }
.muted { color: #667085; font-size: 13px; }
.badge { display: inline-block; padding: 3px 8px; border: 1px solid #ddd; border-radius: 4px; }
.badge.scheduled { background: #eff6ff; border-color: #bfdbfe; color: #1d4ed8; }
.badge.completed { background: #ecfdf3; border-color: #abefc6; color: #067647; }
.badge.cancelled { background: #f2f4f7; border-color: #d0d5dd; color: #344054; }
.error { color: #b42318; }
</style>
