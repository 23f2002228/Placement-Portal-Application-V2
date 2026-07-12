<template>
  <section>
    <h2>Applications</h2>

    <div class="controls">
      <select v-model="selectedJobId">
        <option value="">All jobs</option>
        <option v-for="job in jobs" :key="job.id" :value="job.id">
          {{ job.job_title }}
        </option>
      </select>

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
    <p v-if="message" class="success">{{ message }}</p>

    <table>
      <thead>
        <tr>
          <th>Student</th>
          <th>Job</th>
          <th>Branch</th>
          <th>Year</th>
          <th>CGPA</th>
          <th>Status</th>
          <th>Resume</th>
          <th>Remarks</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="application in applications" :key="application.id">
          <td>
            <b>{{ application.student_name }}</b><br />
            {{ application.student_email }}<br />
            {{ application.student_roll_number }}
          </td>
          <td>{{ application.job_title }}</td>
          <td>{{ application.student_branch }}</td>
          <td>{{ application.student_year }}</td>
          <td>{{ application.student_cgpa }}</td>
          <td>{{ application.status }}</td>
          <td>
            <a v-if="application.student_resume_url" :href="application.student_resume_url" target="_blank">
              Resume
            </a>
            <span v-else>-</span>
          </td>
          <td>{{ application.remarks || '-' }}</td>
          <td class="actions">
            <button v-if="application.status === 'applied'" @click="updateStatus(application.id, 'shortlisted')">
              Shortlist
            </button>
            <button
              v-if="application.status === 'applied' || application.status === 'shortlisted' || application.status === 'interview_scheduled'"
              @click="updateStatus(application.id, 'rejected')"
            >
              Reject
            </button>
            <button
              v-if="application.status === 'shortlisted' || application.status === 'interview_scheduled'"
              @click="updateStatus(application.id, 'selected')"
            >
              Select
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-if="!loading && applications.length === 0">No applications found.</p>
  </section>
</template>

<script>
import axios from 'axios'

export default {
  name: 'CompanyApplications',
  emits: ['dashboard-changed'],
  data() {
    return {
      jobs: [],
      applications: [],
      selectedJobId: '',
      status: '',
      loading: false,
      error: '',
      message: '',
    }
  },
  mounted() {
    this.loadJobs()
    this.loadApplications()
  },
  methods: {
    headers() {
      return {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      }
    },
    async loadJobs() {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/company/jobs', {
          headers: this.headers(),
        })
        this.jobs = response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load jobs.'
      }
    },
    async loadApplications() {
      this.loading = true
      this.error = ''
      this.message = ''

      try {
        let response

        if (this.selectedJobId) {
          response = await axios.get(
            `http://127.0.0.1:5000/api/company/jobs/${this.selectedJobId}/applications`,
            { headers: this.headers() },
          )
          this.applications = this.filterByStatus(response.data)
        } else {
          response = await axios.get('http://127.0.0.1:5000/api/company/applications', {
            params: {
              status: this.status,
            },
            headers: this.headers(),
          })
          this.applications = response.data
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load applications.'
      } finally {
        this.loading = false
      }
    },
    filterByStatus(applications) {
      if (!this.status) return applications
      return applications.filter((application) => application.status === this.status)
    },
    async updateStatus(applicationId, status) {
      let feedback = ''

      if (status === 'rejected') {
        feedback = window.prompt('Feedback for rejection?', '')
        if (!feedback) return
      } else {
        feedback = window.prompt('Optional feedback/remarks?', '') || ''
      }

      this.error = ''
      this.message = ''

      try {
        await axios.patch(
          `http://127.0.0.1:5000/api/company/applications/${applicationId}/status`,
          { status, feedback },
          { headers: this.headers() },
        )
        this.message = 'Application status updated successfully.'
        this.loadApplications()
        this.$emit('dashboard-changed')
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not update application.'
      }
    },
  },
}
</script>

<style scoped>
.controls, .actions { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
select, button { padding: 8px; border: 1px solid #bbb; }
button { cursor: pointer; background: white; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px; border: 1px solid #ddd; text-align: left; vertical-align: top; }
.error { color: #b42318; }
.success { color: #067647; }
</style>
