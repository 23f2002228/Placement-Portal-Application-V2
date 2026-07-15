<template>
  <section class="applications-page">
    <div class="page-header">
      <div>
        <h2>Applications</h2>
        <p>Track your applications, interviews, status changes, and offers.</p>
      </div>

      <button @click="startExport">Export applications CSV</button>
    </div>

    <div class="toolbar">
      <label>
        Status
        <select v-model="status" @change="loadApplications">
          <option value="">All status</option>
          <option value="applied">Applied</option>
          <option value="shortlisted">Shortlisted</option>
          <option value="interview_scheduled">Interview scheduled</option>
          <option value="selected">Selected</option>
          <option value="rejected">Rejected</option>
          <option value="withdrawn">Withdrawn</option>
        </select>
      </label>
    </div>

    <p v-if="loading">Loading applications...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="message" class="success">{{ message }}</p>

    <div class="content-layout">
      <div class="table-panel">
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
            <tr
              v-for="application in applications"
              :key="application.id"
              :class="{ selected: selectedApplication && selectedApplication.id === application.id }"
            >
              <td>{{ application.company_name }}</td>
              <td>{{ application.job_title }}</td>
              <td><span class="status-pill">{{ statusLabel(application.status, application) }}</span></td>
              <td>{{ application.application_date }}</td>
              <td>{{ application.remarks || '-' }}</td>
              <td><button @click="loadApplicationDetails(application.id)">View</button></td>
            </tr>
          </tbody>
        </table>

        <p v-if="!loading && applications.length === 0" class="empty-state">No applications found.</p>
      </div>

      <aside v-if="selectedApplication" class="details">
        <div class="details-header">
          <div>
            <h3>Application Details</h3>
            <p>{{ selectedApplication.company_name }} - {{ selectedApplication.job_title }}</p>
          </div>
          <button class="ghost-button" @click="closeDetails">Close</button>
        </div>

        <div class="details-grid">
          <div class="detail-block">
            <h4>Application</h4>
            <p><b>Company:</b> {{ selectedApplication.company_name }}</p>
            <p><b>Position:</b> {{ selectedApplication.job_title }}</p>
            <p><b>Status:</b> {{ statusLabel(selectedApplication.status, selectedApplication) }}</p>
            <p><b>Applied On:</b> {{ selectedApplication.application_date }}</p>
            <p><b>Remarks:</b> {{ selectedApplication.remarks || '-' }}</p>
          </div>

          <div v-if="selectedApplication.job" class="detail-block">
            <h4>Job Details</h4>
            <p><b>Location:</b> {{ selectedApplication.job.location || '-' }}</p>
            <p><b>Salary:</b> {{ selectedApplication.job.salary || '-' }}</p>
            <p><b>Employment:</b> {{ selectedApplication.job.employment_type || '-' }}</p>
            <p><b>Minimum CGPA:</b> {{ selectedApplication.job.min_cgpa }}</p>
            <p><b>Eligible Branches:</b> {{ selectedApplication.job.eligible_branches }}</p>
          </div>
        </div>

        <div v-if="selectedApplication.placement" class="detail-block">
          <h4>Offer</h4>
          <p><b>Position:</b> {{ selectedApplication.placement.position }}</p>
          <p><b>Salary:</b> {{ selectedApplication.placement.salary }}</p>
          <p><b>Status:</b> {{ statusLabel(selectedApplication.placement.status) }}</p>
          <p><b>Joining Date:</b> {{ selectedApplication.placement.joining_date || '-' }}</p>
        </div>

        <div class="detail-block">
          <h4>Status History</h4>
          <ul v-if="selectedApplication.status_history && selectedApplication.status_history.length">
            <li v-for="history in selectedApplication.status_history" :key="history.id">
              {{ history.changed_at }}:
              {{ statusLabel(history.old_status) || 'New' }} to {{ statusLabel(history.new_status) }}
              <span v-if="history.note">- {{ history.note }}</span>
            </li>
          </ul>
          <p v-else>No status history found.</p>
        </div>

        <div class="detail-block">
          <h4>Interviews</h4>
          <ul v-if="selectedApplication.interviews && selectedApplication.interviews.length">
            <li v-for="interview in selectedApplication.interviews" :key="interview.id">
              {{ interview.round_name || 'Interview' }} -
              {{ interview.scheduled_at }} -
              {{ interview.mode }}
              <span v-if="interview.venue_or_link">({{ interview.venue_or_link }})</span>
            </li>
          </ul>
          <p v-else>No interviews scheduled.</p>
        </div>
      </aside>
    </div>

    <div class="export-panel">
      <ExportJobs
        ref="applicationExports"
        api-base="http://127.0.0.1:5000/api/student"
        :export-types="['application_history']"
        title="Application export jobs"
      />
    </div>
  </section>
</template>

<script>
import axios from 'axios'
import ExportJobs from '@/components/ExportJobs.vue'

export default {
  name: 'StudentApplications',
  components: {
    ExportJobs,
  },
  data() {
    return {
      applications: [],
      selectedApplication: null,
      status: '',
      loading: false,
      error: '',
      message: '',
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
      this.message = ''

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
    closeDetails() {
      this.selectedApplication = null
    },
    async startExport() {
      this.error = ''
      this.message = ''

      try {
        const response = await axios.post(
          'http://127.0.0.1:5000/api/student/exports/application_history',
          {},
          { headers: this.headers() },
        )
        this.message = response.data.message
        if (this.$refs.applicationExports) {
          this.$refs.applicationExports.loadExports()
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not start CSV export.'
      }
    },
    statusLabel(status, application = null) {
      if (!status) return ''
      if (application && application.placement && application.placement.status === 'joined') {
        return 'Placed'
      }

      const labels = {
        applied: 'Applied',
        shortlisted: 'Shortlisted',
        interview_scheduled: 'Interview',
        selected: 'Offer',
        rejected: 'Rejected',
        withdrawn: 'Withdrawn',
        offered: 'Offer',
        accepted: 'Offer Accepted',
        declined: 'Offer Declined',
        joined: 'Placed',
      }

      return labels[status] || status
    },
  },
}
</script>

<style scoped>
.applications-page { display: grid; gap: 18px; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
.page-header h2, .details h3 { margin: 0; }
.page-header p, .details-header p { margin: 4px 0 0; color: #667085; }
.toolbar { display: flex; flex-wrap: wrap; align-items: end; gap: 8px; padding: 12px; border: 1px solid #ddd; background: #f8fafc; }
.toolbar label { display: grid; gap: 4px; color: #344054; font-size: 0.9rem; font-weight: 600; }
select { padding: 8px; border: 1px solid #bbb; }
.primary-button { background: #1d4ed8; border-color: #1d4ed8; color: white; }
.ghost-button { background: #f8fafc; color: #344054; }
.content-layout { display: grid; grid-template-columns: minmax(0, 1fr) 360px; gap: 16px; align-items: start; }
.table-panel { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; background: white; }
th, td { padding: 10px; border: 1px solid #ddd; text-align: left; vertical-align: top; }
th { background: #f8fafc; color: #344054; font-size: 0.85rem; }
tr.selected { background: #eff6ff; }
.status-pill { display: inline-block; padding: 3px 8px; border-radius: 999px; background: #eef2ff; color: #3730a3; font-size: 0.82rem; font-weight: 700; }
.details { display: grid; gap: 14px; border: 1px solid #ddd; padding: 14px; background: white; }
.details-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; border-bottom: 1px solid #eee; padding-bottom: 12px; }
.details-grid { display: grid; gap: 12px; }
.detail-block { padding: 12px; border: 1px solid #eee; background: #fcfcfd; }
.detail-block p { margin: 0 0 6px; }
.detail-block h4 { margin: 0 0 8px; }
.detail-block ul { margin: 0; padding-left: 18px; }
.export-panel { border-top: 1px solid #eee; padding-top: 4px; }
.empty-state { padding: 14px; border: 1px dashed #ccc; color: #667085; text-align: center; }
.error { color: #b42318; }
.success { color: #067647; }
@media (max-width: 1100px) {
  .content-layout { grid-template-columns: 1fr; }
}
@media (max-width: 700px) {
  .page-header, .toolbar { display: grid; }
}
</style>
