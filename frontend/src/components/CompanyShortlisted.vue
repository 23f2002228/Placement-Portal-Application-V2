<template>
  <section>
    <h2>Shortlisted Candidates</h2>
    <p v-if="loading">Loading shortlisted candidates...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="message" class="success">{{ message }}</p>

    <div v-if="selectedApplication" class="schedule-box">
      <h3>Schedule interview for {{ selectedApplication.student_name }}</h3>
      <form class="schedule-form" @submit.prevent="scheduleInterview">
        <label>Date and time<input v-model="interviewForm.scheduled_at" type="datetime-local" required /></label>
        <label>
          Mode
          <select v-model="interviewForm.mode" required>
            <option value="online">Online</option>
            <option value="offline">Offline</option>
          </select>
        </label>
        <label>Venue or link<input v-model="interviewForm.venue_or_link" /></label>
        <label>Round name<input v-model="interviewForm.round_name" /></label>

        <div class="actions">
          <button type="submit">Schedule interview</button>
          <button type="button" @click="cancelSchedule">Cancel</button>
        </div>
      </form>
    </div>

    <table>
      <thead>
        <tr>
          <th>Student</th>
          <th>Job</th>
          <th>Status</th>
          <th>CGPA</th>
          <th>Skills</th>
          <th>Remarks</th>
          <th>Interviews</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="application in applications" :key="application.id">
          <td>
            <b>{{ application.student_name }}</b><br />
            {{ application.student_email }}
          </td>
          <td>{{ application.job_title }}</td>
          <td>{{ application.status }}</td>
          <td>{{ application.student_cgpa }}</td>
          <td>{{ application.student_skills || '-' }}</td>
          <td>{{ application.remarks || '-' }}</td>
          <td>{{ application.interviews.length }}</td>
          <td class="actions">
            <button @click="startSchedule(application)">Schedule</button>
            <button @click="updateStatus(application.id, 'selected')">Select</button>
            <button @click="updateStatus(application.id, 'rejected')">Reject</button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-if="!loading && applications.length === 0">No shortlisted candidates found.</p>
  </section>
</template>

<script>
import axios from 'axios'

export default {
  name: 'CompanyShortlisted',
  emits: ['dashboard-changed'],
  data() {
    return {
      applications: [],
      selectedApplication: null,
      interviewForm: {
        scheduled_at: '',
        mode: 'online',
        venue_or_link: '',
        round_name: '',
      },
      loading: false,
      error: '',
      message: '',
    }
  },
  mounted() {
    this.loadShortlisted()
  },
  methods: {
    headers() {
      return {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      }
    },
    async loadShortlisted() {
      this.loading = true
      this.error = ''

      try {
        const shortlistedResponse = await axios.get('http://127.0.0.1:5000/api/company/applications', {
          params: {
            status: 'shortlisted',
          },
          headers: this.headers(),
        })
        const scheduledResponse = await axios.get('http://127.0.0.1:5000/api/company/applications', {
          params: {
            status: 'interview_scheduled',
          },
          headers: this.headers(),
        })

        this.applications = shortlistedResponse.data.concat(scheduledResponse.data)
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load shortlisted candidates.'
      } finally {
        this.loading = false
      }
    },
    startSchedule(application) {
      this.selectedApplication = application
      this.message = ''
      this.error = ''
    },
    cancelSchedule() {
      this.selectedApplication = null
      this.interviewForm = {
        scheduled_at: '',
        mode: 'online',
        venue_or_link: '',
        round_name: '',
      }
    },
    async scheduleInterview() {
      this.error = ''
      this.message = ''

      try {
        await axios.post(
          `http://127.0.0.1:5000/api/company/applications/${this.selectedApplication.id}/interviews`,
          this.interviewForm,
          { headers: this.headers() },
        )
        this.message = 'Interview scheduled successfully.'
        this.cancelSchedule()
        this.loadShortlisted()
        this.$emit('dashboard-changed')
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not schedule interview.'
      }
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
        this.loadShortlisted()
        this.$emit('dashboard-changed')
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not update application.'
      }
    },
  },
}
</script>

<style scoped>
.schedule-box { border: 1px solid #ddd; padding: 12px; margin-bottom: 16px; }
.schedule-form { display: grid; grid-template-columns: repeat(2, minmax(220px, 1fr)); gap: 12px; }
label { display: grid; gap: 6px; }
input, select { padding: 8px; border: 1px solid #bbb; }
.actions { display: flex; flex-wrap: wrap; gap: 8px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px; border: 1px solid #ddd; text-align: left; vertical-align: top; }
.error { color: #b42318; }
.success { color: #067647; }
@media (max-width: 700px) { .schedule-form { grid-template-columns: 1fr; } }
</style>
