<template>
  <section>
    <h2>Offers</h2>
    <div class="controls">
      <button @click="startExport">Export placements CSV</button>
    </div>

    <p v-if="loading">Loading offers...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="message" class="success">{{ message }}</p>

    <ExportJobs
      ref="placementExports"
      api-base="http://127.0.0.1:5000/api/student"
      :export-types="['placement_history']"
      title="Placement export jobs"
    />

    <table>
      <thead>
        <tr>
          <th>Company</th>
          <th>Position</th>
          <th>Salary</th>
          <th>Status</th>
          <th>Placed At</th>
          <th>Confirmation</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="placement in placements" :key="placement.id">
          <td>{{ placement.company_name }}</td>
          <td>{{ placement.position }}</td>
          <td>{{ placement.salary }}</td>
          <td>{{ placement.status }}</td>
          <td>{{ placement.placed_at }}</td>
          <td><button @click="downloadConfirmation(placement.id)">Download</button></td>
        </tr>
      </tbody>
    </table>

    <p v-if="!loading && placements.length === 0">No offers or placement confirmations found.</p>
  </section>
</template>

<script>
import axios from 'axios'
import ExportJobs from '@/components/ExportJobs.vue'

export default {
  name: 'StudentOffers',
  components: {
    ExportJobs,
  },
  data() {
    return {
      placements: [],
      loading: false,
      error: '',
      message: '',
    }
  },
  mounted() {
    this.loadPlacements()
  },
  methods: {
    headers() {
      return {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      }
    },
    async loadPlacements() {
      this.loading = true
      this.error = ''
      this.message = ''

      try {
        const response = await axios.get('http://127.0.0.1:5000/api/student/placements', {
          headers: this.headers(),
        })
        this.placements = response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load offers.'
      } finally {
        this.loading = false
      }
    },
    async downloadConfirmation(placementId) {
      this.error = ''

      try {
        const response = await axios.get(
          `http://127.0.0.1:5000/api/student/placements/${placementId}/confirmation`,
          {
            headers: this.headers(),
            responseType: 'blob',
          },
        )
        const fileUrl = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = fileUrl
        link.setAttribute('download', `placement-confirmation-${placementId}.txt`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(fileUrl)
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not download confirmation.'
      }
    },
    async startExport() {
      this.error = ''
      this.message = ''

      try {
        const response = await axios.post(
          'http://127.0.0.1:5000/api/student/exports/placement_history',
          {},
          { headers: this.headers() },
        )
        this.message = response.data.message
        if (this.$refs.placementExports) {
          this.$refs.placementExports.loadExports()
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not start CSV export.'
      }
    },
  },
}
</script>

<style scoped>
.controls { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px; border: 1px solid #ddd; text-align: left; vertical-align: top; }
.error { color: #b42318; }
.success { color: #067647; }
</style>
