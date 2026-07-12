<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div>
        <h1>Company Dashboard</h1>
        <p>{{ email }}</p>
      </div>
      <button @click="$emit('logout')">Logout</button>
    </header>

    <nav class="tabs">
      <button @click="activeTab = 'overview'">Overview</button>
      <button @click="activeTab = 'profile'">Profile</button>
      <button @click="activeTab = 'jobs'">Jobs</button>
      <button @click="activeTab = 'applications'">Applications</button>
      <button @click="activeTab = 'shortlisted'">Shortlisted</button>
      <button @click="activeTab = 'interviews'">Interviews</button>
    </nav>

    <main class="dashboard-body">
      <CompanyOverview v-if="activeTab === 'overview'" :key="dashboardVersion" />
      <CompanyProfile v-if="activeTab === 'profile'" />
      <CompanyJobs v-if="activeTab === 'jobs'" @dashboard-changed="refreshDashboard" />
      <CompanyApplications
        v-if="activeTab === 'applications'"
        @dashboard-changed="refreshDashboard"
      />
      <CompanyShortlisted
        v-if="activeTab === 'shortlisted'"
        @dashboard-changed="refreshDashboard"
      />
      <CompanyInterviews v-if="activeTab === 'interviews'" />
    </main>
  </div>
</template>

<script>
import CompanyApplications from '@/components/CompanyApplications.vue'
import CompanyInterviews from '@/components/CompanyInterviews.vue'
import CompanyJobs from '@/components/CompanyJobs.vue'
import CompanyOverview from '@/components/CompanyOverview.vue'
import CompanyProfile from '@/components/CompanyProfile.vue'
import CompanyShortlisted from '@/components/CompanyShortlisted.vue'

export default {
  name: 'CompanyDashboard',
  components: {
    CompanyApplications,
    CompanyInterviews,
    CompanyJobs,
    CompanyOverview,
    CompanyProfile,
    CompanyShortlisted,
  },
  emits: ['logout'],
  data() {
    return {
      activeTab: 'overview',
      dashboardVersion: 0,
      email: localStorage.getItem('email') || 'Company',
    }
  },
  methods: {
    refreshDashboard() {
      this.dashboardVersion += 1
    },
  },
}
</script>

<style scoped>
.dashboard { min-height: 100vh; padding: 24px; }
.dashboard-header { display: flex; justify-content: space-between; gap: 16px; align-items: center; margin-bottom: 20px; }
.dashboard-header h1 { margin: 0; }
.dashboard-header p { margin: 4px 0 0; color: #667085; }
.tabs { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
.dashboard-body { border: 1px solid #ddd; background: white; padding: 18px; overflow-x: auto; }
button { padding: 9px 12px; border: 1px solid #bbb; background: white; cursor: pointer; }
</style>
