<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div>
        <h1>Student Dashboard</h1>
        <p>{{ email }}</p>
      </div>
      <button @click="$emit('logout')">Logout</button>
    </header>

    <section class="simple-card">
      <nav class="tabs">
        <button @click="activeTab = 'overview'">Overview</button>
        <button @click="activeTab = 'profile'">Profile</button>
        <button @click="activeTab = 'jobs'">Jobs</button>
        <button @click="activeTab = 'applications'">Applications</button>
        <button @click="activeTab = 'interviews'">Interviews</button>
        <button @click="activeTab = 'offers'">Offers</button>
      </nav>

      <main class="dashboard-body">
        <StudentOverview v-if="activeTab === 'overview'" :key="dashboardVersion" />
        <StudentProfile v-if="activeTab === 'profile'" />
        <StudentJobs v-if="activeTab === 'jobs'" @dashboard-changed="refreshDashboard" />
        <StudentApplications v-if="activeTab === 'applications'" />
        <StudentInterviews v-if="activeTab === 'interviews'" />
        <StudentOffers v-if="activeTab === 'offers'" />
      </main>
    </section>
  </div>
</template>

<script>
import StudentApplications from '@/components/StudentApplications.vue'
import StudentInterviews from '@/components/StudentInterviews.vue'
import StudentJobs from '@/components/StudentJobs.vue'
import StudentOffers from '@/components/StudentOffers.vue'
import StudentOverview from '@/components/StudentOverview.vue'
import StudentProfile from '@/components/StudentProfile.vue'

export default {
  name: 'StudentDashboard',
  components: {
    StudentApplications,
    StudentInterviews,
    StudentJobs,
    StudentOffers,
    StudentOverview,
    StudentProfile,
  },
  emits: ['logout'],
  data() {
    return {
      activeTab: 'overview',
      dashboardVersion: 0,
      email: localStorage.getItem('email') || 'Student',
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
.simple-card { border: 1px solid #ddd; background: white; padding: 18px; overflow-x: auto; }
.tabs { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
.dashboard-body { overflow-x: auto; }
button { padding: 9px 12px; border: 1px solid #bbb; background: white; cursor: pointer; }
</style>
