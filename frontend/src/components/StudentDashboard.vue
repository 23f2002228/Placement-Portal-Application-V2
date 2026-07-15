<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div>
        <h1>Student Dashboard</h1>
        <p>{{ email }}</p>
      </div>
      <div class="header-actions">
        <NotificationBell />
        <button @click="$emit('logout')">Logout</button>
      </div>
    </header>

    <section class="simple-card">
      <nav class="tabs">
        <button :class="{ active: activeTab === 'overview' }" @click="activeTab = 'overview'">Overview</button>
        <button :class="{ active: activeTab === 'profile' }" @click="activeTab = 'profile'">Profile</button>
        <button :class="{ active: activeTab === 'jobs' }" @click="activeTab = 'jobs'">Jobs</button>
        <button :class="{ active: activeTab === 'applications' }" @click="activeTab = 'applications'">Applications</button>
        <button :class="{ active: activeTab === 'interviews' }" @click="activeTab = 'interviews'">Interviews</button>
        <button :class="{ active: activeTab === 'offers' }" @click="activeTab = 'offers'">Offers</button>
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
import NotificationBell from '@/components/NotificationBell.vue'
import StudentOffers from '@/components/StudentOffers.vue'
import StudentOverview from '@/components/StudentOverview.vue'
import StudentProfile from '@/components/StudentProfile.vue'

export default {
  name: 'StudentDashboard',
  components: {
    NotificationBell,
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
