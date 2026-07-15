<template>
  <section class="applications-page">
    <div class="page-header">
      <div>
        <h2>Applications</h2>
        <p>Review candidates, export records, and open one application at a time.</p>
      </div>

      <div class="export-actions">
        <button @click="startExport('application_history')">Export applications CSV</button>
        <button @click="startExport('placement_history')">Export placements CSV</button>
      </div>
    </div>

    <div class="toolbar">
      <label>
        Job
        <select v-model="selectedJobId">
          <option value="">All jobs</option>
          <option v-for="job in jobs" :key="job.id" :value="job.id">
            {{ job.job_title }}
          </option>
        </select>
      </label>

      <label>
        Status
        <select v-model="status">
          <option value="">All status</option>
          <option value="applied">Applied</option>
          <option value="shortlisted">Shortlisted</option>
          <option value="interview_scheduled">Interview scheduled</option>
          <option value="selected">Selected</option>
          <option value="rejected">Rejected</option>
          <option value="withdrawn">Withdrawn</option>
        </select>
      </label>

      <button class="primary-button" @click="loadApplications">Load applications</button>
    </div>

    <p v-if="loading">Loading applications...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="message" class="success">{{ message }}</p>

    <div class="content-layout">
      <div class="table-panel">
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
            <tr
              v-for="application in applications"
              :key="application.id"
              :class="{ selected: selectedApplication && selectedApplication.id === application.id }"
            >
              <td>
                <b>{{ application.student_name }}</b><br />
                <span class="muted">{{ application.student_email }}</span><br />
                <span class="muted">{{ application.student_roll_number }}</span>
              </td>
              <td>{{ application.job_title }}</td>
              <td>{{ application.student_branch }}</td>
              <td>{{ application.student_year }}</td>
              <td>{{ application.student_cgpa }}</td>
              <td><span class="status-pill">{{ statusLabel(application.status, application) }}</span></td>
              <td>
                <a v-if="application.student_resume_url" :href="application.student_resume_url" target="_blank">
                  Resume
                </a>
                <span v-else>-</span>
              </td>
              <td>{{ application.remarks || '-' }}</td>
              <td class="actions">
                <button @click="loadApplicationDetails(application.id)">
                  View
                </button>
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

        <p v-if="!loading && applications.length === 0" class="empty-state">No applications found.</p>
      </div>

      <aside v-if="selectedApplication" class="details">
        <div class="details-header">
          <div>
            <h3>Application Details</h3>
            <p>{{ selectedApplication.student_name }} for {{ selectedApplication.job_title }}</p>
          </div>
          <button class="ghost-button" @click="closeDetails">Close</button>
        </div>

        <div class="details-grid">
          <div class="detail-block">
            <h4>Student Profile</h4>
            <p><b>Name:</b> {{ selectedApplication.student_name }}</p>
            <p><b>Email:</b> {{ selectedApplication.student_email }}</p>
            <p><b>Roll No.:</b> {{ selectedApplication.student_roll_number }}</p>
            <p><b>Branch:</b> {{ selectedApplication.student_branch }}</p>
            <p><b>Year:</b> {{ selectedApplication.student_year }}</p>
            <p><b>CGPA:</b> {{ selectedApplication.student_cgpa }}</p>
            <p><b>Phone:</b> {{ selectedApplication.student_phone || '-' }}</p>
            <p><b>Skills:</b> {{ selectedApplication.student_skills || '-' }}</p>
            <p><b>Experience:</b> {{ selectedApplication.student_experience || '-' }}</p>
            <p>
              <b>Resume:</b>
              <a v-if="selectedApplication.student_resume_url" :href="selectedApplication.student_resume_url" target="_blank">
                Open resume
              </a>
              <span v-else>-</span>
            </p>
          </div>

          <div class="detail-block">
            <h4>Application</h4>
            <p><b>Job:</b> {{ selectedApplication.job_title }}</p>
            <p><b>Status:</b> {{ statusLabel(selectedApplication.status, selectedApplication) }}</p>
            <p><b>Applied On:</b> {{ selectedApplication.application_date }}</p>
            <p><b>Remarks:</b> {{ selectedApplication.remarks || '-' }}</p>
            <p v-if="selectedApplication.placement">
              <b>Offer:</b>
              {{ selectedApplication.placement.position }} -
              {{ selectedApplication.placement.salary }}
              ({{ statusLabel(selectedApplication.placement.status) }})
            </p>
          </div>
        </div>

        <div class="detail-block">
          <h4>Status History</h4>
          <ul v-if="selectedApplication.status_history && selectedApplication.status_history.length">
            <li v-for="history in selectedApplication.status_history" :key="history.id">
              {{ history.changed_at }}:
              {{ statusLabel(history.old_status) || 'New' }} to {{ statusLabel(history.new_status) }}
              <span v-if="history.changed_by_email">by {{ history.changed_by_email }}</span>
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
        ref="companyExports"
        api-base="http://127.0.0.1:5000/api/company"
        :export-types="['application_history', 'placement_history']"
        title="Export jobs"
      />
    </div>
  </section>
</template>

<script>
import axios from 'axios'
import ExportJobs from '@/components/ExportJobs.vue'

export default {
  name: 'CompanyApplications',
  components: {
    ExportJobs,
  },
  emits: ['dashboard-changed'],
  data() {
    return {
      jobs: [],
      applications: [],
      selectedApplication: null,
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
        this.loadApplicationDetails(applicationId)
        this.$emit('dashboard-changed')
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not update application.'
      }
    },
    async loadApplicationDetails(applicationId) {
      this.error = ''

      try {
        const response = await axios.get(
          `http://127.0.0.1:5000/api/company/applications/${applicationId}`,
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
    async startExport(exportType) {
      this.error = ''
      this.message = ''

      try {
        const response = await axios.post(
          `http://127.0.0.1:5000/api/company/exports/${exportType}`,
          {},
          { headers: this.headers() },
        )
        this.message = response.data.message
        if (this.$refs.companyExports) {
          this.$refs.companyExports.loadExports()
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
.page-header p, .details-header p, .muted { color: #667085; }
.page-header p, .details-header p { margin: 4px 0 0; }
.toolbar, .export-actions, .actions { display: flex; flex-wrap: wrap; gap: 8px; }
.toolbar { align-items: end; padding: 12px; border: 1px solid #ddd; background: #f8fafc; }
.toolbar label { display: grid; gap: 4px; color: #344054; font-size: 0.9rem; font-weight: 600; }
select, button { padding: 8px; border: 1px solid #bbb; }
button { cursor: pointer; background: white; }
.primary-button { background: #1d4ed8; border-color: #1d4ed8; color: white; }
.ghost-button { background: #f8fafc; }
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
  .page-header { display: grid; }
  .export-actions, .toolbar { display: grid; }
}
</style>
