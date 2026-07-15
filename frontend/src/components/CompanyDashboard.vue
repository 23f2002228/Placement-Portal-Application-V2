<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div>
        <h1>Company Dashboard</h1>
        <p>{{ email }}</p>
      </div>
      <div class="header-actions">
        <NotificationBell />
        <button @click="$emit('logout')">Logout</button>
      </div>
    </header>

    <nav class="tabs">
      <button :class="{ active: activeTab === 'overview' }" @click="activeTab = 'overview'">Overview</button>
      <button :class="{ active: activeTab === 'profile' }" @click="activeTab = 'profile'">Profile</button>
      <button :class="{ active: activeTab === 'jobs' }" @click="activeTab = 'jobs'">Jobs</button>
      <button :class="{ active: activeTab === 'applications' }" @click="activeTab = 'applications'">Applications</button>
      <button :class="{ active: activeTab === 'shortlisted' }" @click="activeTab = 'shortlisted'">Shortlisted</button>
      <button :class="{ active: activeTab === 'interviews' }" @click="activeTab = 'interviews'">Interviews</button>
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
import NotificationBell from '@/components/NotificationBell.vue'
import CompanyOverview from '@/components/CompanyOverview.vue'
import CompanyProfile from '@/components/CompanyProfile.vue'
import CompanyShortlisted from '@/components/CompanyShortlisted.vue'

export default {
  name: 'CompanyDashboard',
  components: {
    CompanyApplications,
    CompanyInterviews,
    CompanyJobs,
    NotificationBell,
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
