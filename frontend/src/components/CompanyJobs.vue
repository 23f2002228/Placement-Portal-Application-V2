<template>
  <section>
    <h2>Jobs</h2>
    <p v-if="message" class="success">{{ message }}</p>
    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="!showJobForm">
      <div class="controls">
        <select v-model="status">
          <option value="">All jobs</option>
          <option value="pending">Pending admin approval</option>
          <option value="active">Active</option>
          <option value="rejected">Rejected</option>
          <option value="closed">Closed</option>
        </select>
        <button @click="loadJobs">Load jobs</button>
        <button @click="openCreateForm">Create job</button>
      </div>

      <p v-if="loading">Loading jobs...</p>

      <table>
        <thead>
          <tr>
            <th>Job Title</th>
            <th>Location</th>
            <th>Salary</th>
            <th>Status</th>
            <th>Applications</th>
            <th>Deadline</th>
            <th>Rejection Reason</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in jobs" :key="job.id">
            <td>{{ job.job_title }}</td>
            <td>{{ job.location }}</td>
            <td>{{ job.salary }}</td>
            <td>{{ job.status }}</td>
            <td>{{ job.applications_count }}</td>
            <td>{{ job.application_deadline }}</td>
            <td>{{ job.rejection_reason || '-' }}</td>
            <td class="actions">
              <button v-if="job.status !== 'rejected' && job.status !== 'closed'" @click="startEdit(job)">
                Edit
              </button>
              <button v-if="job.status === 'active'" @click="changeJobStatus(job.id, 'closed')">
                Close
              </button>
              <button v-if="job.status === 'closed'" @click="changeJobStatus(job.id, 'active')">
                Reactivate
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <p v-if="!loading && jobs.length === 0">No jobs found.</p>
    </div>

    <form v-else class="job-form" @submit.prevent="saveJob">
      <h3>{{ editingJobId ? 'Edit job' : 'Create job' }}</h3>

      <label>Job title<input v-model="form.job_title" required /></label>
      <label>Location<input v-model="form.location" required /></label>
      <label>Salary<input v-model.number="form.salary" type="number" min="0" required /></label>
      <label>Employment type<input v-model="form.employment_type" required /></label>
      <label>Experience required<input v-model="form.experience_required" required /></label>
      <label>Minimum CGPA<input v-model.number="form.min_cgpa" type="number" min="0" max="10" step="0.1" required /></label>
      <label>Eligible branches<input v-model="form.eligible_branches" required /></label>
      <label>Eligible year<input v-model.number="form.eligible_year" type="number" min="1" max="4" required /></label>
      <label>Application deadline<input v-model="form.application_deadline" type="datetime-local" required /></label>
      <label>Drive date<input v-model="form.drive_date" type="datetime-local" /></label>
      <label class="wide">Skills required<textarea v-model="form.skills_required" rows="2" required></textarea></label>
      <label class="wide">Benefits<textarea v-model="form.benefits" rows="2" required></textarea></label>
      <label class="wide">Job description<textarea v-model="form.job_description" rows="3" required></textarea></label>

      <div class="form-actions">
        <button type="submit">{{ editingJobId ? 'Update job' : 'Create job' }}</button>
        <button v-if="editingJobId" type="button" @click="resetForm">Cancel edit</button>
        <button v-else type="button" @click="resetForm">Cancel</button>
      </div>
    </form>
  </section>
</template>

<script>
import axios from 'axios'

export default {
  name: 'CompanyJobs',
  emits: ['dashboard-changed'],
  data() {
    return {
      jobs: [],
      status: '',
      showJobForm: false,
      editingJobId: null,
      loading: false,
      error: '',
      message: '',
      form: this.emptyForm(),
    }
  },
  mounted() {
    this.loadJobs()
  },
  methods: {
    emptyForm() {
      return {
        job_title: '',
        job_description: '',
        location: '',
        salary: '',
        skills_required: '',
        experience_required: '',
        benefits: '',
        employment_type: '',
        min_cgpa: '',
        eligible_branches: '',
        eligible_year: '',
        application_deadline: '',
        drive_date: '',
      }
    },
    headers() {
      return {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      }
    },
    async loadJobs() {
      this.loading = true
      this.error = ''

      try {
        const response = await axios.get('http://127.0.0.1:5000/api/company/jobs', {
          params: {
            status: this.status,
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
    async saveJob() {
      this.error = ''
      this.message = ''

      try {
        if (this.editingJobId) {
          await axios.patch(`http://127.0.0.1:5000/api/company/jobs/${this.editingJobId}`, this.form, {
            headers: this.headers(),
          })
          this.message = 'Job updated successfully.'
        } else {
          await axios.post('http://127.0.0.1:5000/api/company/jobs', this.form, {
            headers: this.headers(),
          })
          this.message = 'Job created and sent for admin approval.'
        }

        this.resetForm()
        this.loadJobs()
        this.$emit('dashboard-changed')
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not save job.'
      }
    },
    openCreateForm() {
      this.resetForm()
      this.showJobForm = true
    },
    startEdit(job) {
      this.showJobForm = true
      this.editingJobId = job.id
      this.form = {
        job_title: job.job_title || '',
        job_description: job.job_description || '',
        location: job.location || '',
        salary: job.salary || '',
        skills_required: job.skills_required || '',
        experience_required: job.experience_required || '',
        benefits: job.benefits || '',
        employment_type: job.employment_type || '',
        min_cgpa: job.min_cgpa || '',
        eligible_branches: job.eligible_branches || '',
        eligible_year: job.eligible_year || '',
        application_deadline: this.toInputDate(job.application_deadline),
        drive_date: this.toInputDate(job.drive_date),
      }
    },
    resetForm() {
      this.showJobForm = false
      this.editingJobId = null
      this.form = this.emptyForm()
    },
    toInputDate(value) {
      if (!value) return ''
      return String(value).slice(0, 16)
    },
    async changeJobStatus(jobId, status) {
      this.error = ''
      this.message = ''

      try {
        await axios.patch(`http://127.0.0.1:5000/api/company/jobs/${jobId}/status`, { status }, {
          headers: this.headers(),
        })
        this.message = 'Job status updated successfully.'
        this.loadJobs()
        this.$emit('dashboard-changed')
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not update job status.'
      }
    },
  },
}
</script>

<style scoped>
.job-form { display: grid; grid-template-columns: repeat(2, minmax(220px, 1fr)); gap: 12px; margin-bottom: 20px; }
.job-form h3, .wide, .form-actions { grid-column: 1 / -1; }
label { display: grid; gap: 6px; }
input, textarea, select, button { padding: 8px; border: 1px solid #bbb; }
button { cursor: pointer; background: white; }
.controls, .form-actions, .actions { display: flex; flex-wrap: wrap; gap: 8px; }
.controls { margin-bottom: 12px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px; border: 1px solid #ddd; text-align: left; vertical-align: top; }
.error { color: #b42318; }
.success { color: #067647; }
@media (max-width: 700px) { .job-form { grid-template-columns: 1fr; } }
</style>
