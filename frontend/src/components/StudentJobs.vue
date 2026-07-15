<template>
  <section>
    <h2>Jobs</h2>
    <p v-if="message" class="success">{{ message }}</p>
    <p v-if="error" class="error">{{ error }}</p>

    <div class="controls">
      <input v-model="search" placeholder="Search company, position, or skills" @keyup.enter="loadJobs" />
      <button @click="loadJobs">Search</button>
    </div>

    <p v-if="loading">Loading jobs...</p>

    <table>
      <thead>
        <tr>
          <th>Company</th>
          <th>Position</th>
          <th>Location</th>
          <th>Salary</th>
          <th>Skills</th>
          <th>Eligibility</th>
          <th>Deadline</th>
          <th>Application</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="job in jobs" :key="job.id">
          <td>{{ job.company_name }}</td>
          <td>
            <b>{{ job.job_title }}</b><br />
            {{ job.employment_type }}
          </td>
          <td>{{ job.location }}</td>
          <td>{{ job.salary }}</td>
          <td>{{ job.skills_required }}</td>
          <td>
            {{ job.eligibility_message }}<br />
            <small>CGPA {{ job.min_cgpa }}, Year {{ job.eligible_year }}, {{ job.eligible_branches }}</small>
          </td>
          <td>{{ job.application_deadline }}</td>
          <td>
            <span v-if="job.already_applied">{{ job.application_status }}</span>
            <button v-else :disabled="!job.eligible" @click="applyForJob(job.id)">Apply</button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-if="!loading && jobs.length === 0">No jobs found.</p>
  </section>
</template>

<script>
import axios from 'axios'

export default {
  name: 'StudentJobs',
  emits: ['dashboard-changed'],
  data() {
    return {
      jobs: [],
      search: '',
      loading: false,
      error: '',
      message: '',
    }
  },
  mounted() {
    this.loadJobs()
  },
  methods: {
    headers() {
      return {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      }
    },
    async loadJobs() {
      this.loading = true
      this.error = ''

      try {
        const response = await axios.get('http://127.0.0.1:5000/api/student/jobs', {
          params: {
            search: this.search,
          },
          headers: this.headers(),
        })
        this.jobs = response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load jobs.'
      } finally {
        this.loading = false
      }
    },
    async applyForJob(jobId) {
      this.error = ''
      this.message = ''

      try {
        await axios.post(`http://127.0.0.1:5000/api/student/jobs/${jobId}/apply`, {}, {
          headers: this.headers(),
        })
        this.message = 'Application submitted successfully.'
        this.loadJobs()
        this.$emit('dashboard-changed')
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not apply for this job.'
      }
    },
  },
}
</script>

<style scoped>
.controls { margin-bottom: 12px; }
input { min-width: min(360px, 100%); }
</style>
