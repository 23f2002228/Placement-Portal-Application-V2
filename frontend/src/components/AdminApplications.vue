<template>
  <section class="applications-page">
    <div class="page-header">
      <div>
        <h2>Applications</h2>
        <p>Search applications and inspect student, drive, interview, and offer details.</p>
      </div>
    </div>

    <div class="toolbar">
      <label>
        Search
        <input v-model="search" placeholder="Student, company, job" @keyup.enter="loadApplications" />
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

      <button class="primary-button" @click="loadApplications">Search</button>
    </div>

    <p v-if="loading">Loading applications...</p>
    <p v-if="error" class="error">{{ error }}</p>

    <div class="content-layout">
      <div class="table-panel">
        <table>
          <thead>
            <tr>
              <th>Student</th>
              <th>Roll No.</th>
              <th>Company</th>
              <th>Job Title</th>
              <th>Status</th>
              <th>Date</th>
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
              <td>{{ application.student_name }}</td>
              <td>{{ application.student_roll_number }}</td>
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
            <h4>Drive</h4>
            <p><b>Company:</b> {{ selectedApplication.company_name }}</p>
            <p><b>Job:</b> {{ selectedApplication.job_title }}</p>
            <p><b>Status:</b> {{ statusLabel(selectedApplication.status, selectedApplication) }}</p>
            <p><b>Applied On:</b> {{ selectedApplication.application_date }}</p>
            <p><b>Remarks:</b> {{ selectedApplication.remarks || '-' }}</p>
            <p v-if="selectedApplication.drive"><b>Drive Status:</b> {{ selectedApplication.drive.status }}</p>
            <p v-if="selectedApplication.drive"><b>Eligible Branches:</b> {{ selectedApplication.drive.eligible_branches }}</p>
            <p v-if="selectedApplication.drive"><b>Minimum CGPA:</b> {{ selectedApplication.drive.min_cgpa }}</p>
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
  </section>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AdminApplications',
  data() {
    return {
      applications: [],
      selectedApplication: null,
      search: '',
      status: '',
      loading: false,
      error: '',
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

      try {
        const response = await axios.get('http://127.0.0.1:5000/api/admin/applications', {
          params: {
            search: this.search,
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
          `http://127.0.0.1:5000/api/admin/applications/${applicationId}`,
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
.page-header h2, .details h3 { margin: 0; }
.page-header p, .details-header p { margin: 4px 0 0; color: #667085; }
.toolbar { display: flex; flex-wrap: wrap; align-items: end; gap: 8px; padding: 12px; border: 1px solid #ddd; background: #f8fafc; }
.toolbar label { display: grid; gap: 4px; color: #344054; font-size: 0.9rem; font-weight: 600; }
input, select { padding: 8px; border: 1px solid #bbb; }
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
.empty-state { padding: 14px; border: 1px dashed #ccc; color: #667085; text-align: center; }
.error { color: #b42318; }
@media (max-width: 1100px) {
  .content-layout { grid-template-columns: 1fr; }
}
@media (max-width: 700px) {
  .toolbar { display: grid; }
}
</style>
