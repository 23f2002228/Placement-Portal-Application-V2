<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div>
        <h1>Admin Dashboard</h1>
        <p>{{ email }}</p>
      </div>
      <button @click="$emit('logout')">Logout</button>
    </header>

    <nav class="tabs">
      <button @click="activeTab = 'overview'">Overview</button>
      <button @click="activeTab = 'companies'">Companies</button>
      <button @click="activeTab = 'students'">Students</button>
      <button @click="activeTab = 'drives'">Drives</button>
      <button @click="activeTab = 'applications'">Applications</button>
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

export default {
  name: 'AdminDashboard',
  components: {
    AdminApplications,
    AdminCompanies,
    AdminDrives,
    AdminOverview,
    AdminStudents,
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

<style scoped>
.dashboard { min-height: 100vh; padding: 24px; }
.dashboard-header { display: flex; justify-content: space-between; gap: 16px; align-items: center; margin-bottom: 20px; }
.dashboard-header h1 { margin: 0; }
.dashboard-header p { margin: 4px 0 0; color: #667085; }
.tabs { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
button { padding: 9px 12px; border: 1px solid #bbb; background: white; cursor: pointer; }
.dashboard-body { border: 1px solid #ddd; background: white; padding: 18px; overflow-x: auto; }
</style>
