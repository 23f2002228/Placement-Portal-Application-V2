<template>
  <section class="export-panel">
    <div class="export-header">
      <h3>{{ title }}</h3>
      <button type="button" @click="loadExports">Refresh exports</button>
    </div>

    <p v-if="loading">Loading exports...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="!loading && filteredExports.length === 0">No export jobs found.</p>

    <table v-if="filteredExports.length">
      <thead>
        <tr>
          <th>Export</th>
          <th>Status</th>
          <th>Requested</th>
          <th>Completed</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="exportJob in filteredExports" :key="exportJob.id">
          <td>{{ exportLabel(exportJob.export_type) }}</td>
          <td>{{ statusLabel(exportJob.status) }}</td>
          <td>{{ exportJob.requested_at || '-' }}</td>
          <td>{{ exportJob.completed_at || '-' }}</td>
          <td>
            <button
              v-if="exportJob.status === 'completed'"
              type="button"
              @click="downloadExport(exportJob)"
            >
              Download
            </button>
            <span v-else-if="exportJob.status === 'failed'" class="error">
              {{ exportJob.error_message || 'Export failed' }}
            </span>
            <span v-else>Processing...</span>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ExportJobs',
  props: {
    apiBase: {
      type: String,
      required: true,
    },
    exportTypes: {
      type: Array,
      default: () => [],
    },
    title: {
      type: String,
      default: 'Export jobs',
    },
  },
  data() {
    return {
      exports: [],
      loading: false,
      error: '',
      pollTimer: null,
    }
  },
  computed: {
    filteredExports() {
      if (!this.exportTypes.length) {
        return this.exports
      }

      return this.exports.filter((exportJob) => this.exportTypes.includes(exportJob.export_type))
    },
    hasActiveExports() {
      return this.filteredExports.some((exportJob) => {
        return exportJob.status === 'pending' || exportJob.status === 'running'
      })
    },
  },
  mounted() {
    this.loadExports()
  },
  beforeUnmount() {
    this.stopPolling()
  },
  methods: {
    headers() {
      return {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      }
    },
    async loadExports() {
      this.loading = this.exports.length === 0
      this.error = ''

      try {
        const response = await axios.get(`${this.apiBase}/exports`, {
          headers: this.headers(),
        })
        this.exports = response.data

        if (this.hasActiveExports) {
          this.startPolling()
        } else {
          this.stopPolling()
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load export jobs.'
        this.stopPolling()
      } finally {
        this.loading = false
      }
    },
    startPolling() {
      if (this.pollTimer) {
        return
      }

      this.pollTimer = window.setInterval(this.loadExports, 3000)
    },
    stopPolling() {
      if (!this.pollTimer) {
        return
      }

      window.clearInterval(this.pollTimer)
      this.pollTimer = null
    },
    async downloadExport(exportJob) {
      this.error = ''

      try {
        const response = await axios.get(`${this.apiBase}/exports/${exportJob.id}/download`, {
          headers: this.headers(),
          responseType: 'blob',
        })
        const fileUrl = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = fileUrl
        link.setAttribute('download', `export-${exportJob.id}-${exportJob.export_type}.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(fileUrl)
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not download export.'
      }
    },
    exportLabel(exportType) {
      const labels = {
        application_history: 'Application history',
        placement_history: 'Placement history',
      }

      return labels[exportType] || exportType
    },
    statusLabel(status) {
      const labels = {
        pending: 'Pending',
        running: 'Running',
        completed: 'Completed',
        failed: 'Failed',
      }

      return labels[status] || status
    },
  },
}
</script>

<style scoped>
.export-panel {
  margin: 16px 0;
  border: 1px solid #ddd;
  padding: 14px;
}
.export-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 10px;
}
.export-header h3 { margin: 0; }
button {
  padding: 8px;
  border: 1px solid #bbb;
  background: white;
  cursor: pointer;
}
table { width: 100%; border-collapse: collapse; }
th, td {
  padding: 8px;
  border: 1px solid #ddd;
  text-align: left;
  vertical-align: top;
}
.error { color: #b42318; }
</style>
