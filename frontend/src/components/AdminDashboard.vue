<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div>
        <h1>Admin Dashboard</h1>
        <p>{{ email }}</p>
      </div>
      <div class="header-actions">
        <NotificationBell />
        <button @click="$emit('logout')">Logout</button>
      </div>
    </header>

    <nav class="tabs">
      <button :class="{ active: activeTab === 'overview' }" @click="activeTab = 'overview'">Overview</button>
      <button :class="{ active: activeTab === 'companies' }" @click="activeTab = 'companies'">Companies</button>
      <button :class="{ active: activeTab === 'students' }" @click="activeTab = 'students'">Students</button>
      <button :class="{ active: activeTab === 'drives' }" @click="activeTab = 'drives'">Drives</button>
      <button :class="{ active: activeTab === 'applications' }" @click="activeTab = 'applications'">Applications</button>
    </nav>

    <main class="dashboard-body">
      <AdminOverview v-if="activeTab === 'overview'" :key="dashboardVersion" />
      <AdminCompanies v-if="activeTab === 'companies'" @dashboard-changed="refreshDashboard" />
      <AdminStudents v-if="activeTab === 'students'" @dashboard-changed="refreshDashboard" />
      <AdminDrives v-if="activeTab === 'drives'" @dashboard-changed="refreshDashboard" />
      <AdminApplications v-if="activeTab === 'applications'" />
    </main>
  </div>
</template>

<script>
import AdminApplications from '@/components/AdminApplications.vue'
import AdminCompanies from '@/components/AdminCompanies.vue'
import AdminDrives from '@/components/AdminDrives.vue'
import AdminOverview from '@/components/AdminOverview.vue'
import AdminStudents from '@/components/AdminStudents.vue'
import NotificationBell from '@/components/NotificationBell.vue'

export default {
  name: 'AdminDashboard',
  components: {
    AdminApplications,
    AdminCompanies,
    AdminDrives,
    AdminOverview,
    AdminStudents,
    NotificationBell,
  },
  emits: ['logout'],
  data() {
    return {
      activeTab: 'overview',
      dashboardVersion: 0,
      email: localStorage.getItem('email') || 'Admin',
    }
  },
  methods: {
    refreshDashboard() {
      this.dashboardVersion += 1
    },
  },
}
</script>
