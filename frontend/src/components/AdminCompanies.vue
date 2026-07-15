<template>
  <section>
    <h2>Companies</h2>

    <div class="controls">
      <select v-model="searchBy">
        <option value="all">Search all</option>
        <option value="name">Name</option>
        <option value="industry">Industry</option>
        <option value="location">Location</option>
        <option value="email">Email</option>
      </select>
      <input v-model="search" :placeholder="searchPlaceholder" @keyup.enter="loadCompanies" />
      <select v-model="status">
        <option value="">All status</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
      </select>
      <button @click="loadCompanies">Search</button>
    </div>

    <p v-if="loading">Loading companies...</p>
    <p v-if="error" class="error">{{ error }}</p>

    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Industry</th>
          <th>Location</th>
          <th>Email</th>
          <th>Status</th>
          <th>Account</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="company in companies" :key="company.id">
          <td>{{ company.company_name }}</td>
          <td>{{ company.industry }}</td>
          <td>{{ company.location }}</td>
          <td>{{ company.email }}</td>
          <td>{{ company.approval_status }}</td>
          <td>{{ accountStatus(company) }}</td>
          <td class="actions">
            <button @click="approveCompany(company.id)">Approve</button>
            <button @click="rejectCompany(company.id)">Reject</button>
            <button @click="deactivateUser(company.user_id)">Deactivate</button>
            <button @click="blacklistUser(company.user_id)">Blacklist</button>
            <button @click="unblacklistUser(company.user_id)">Unblacklist</button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AdminCompanies',
  emits: ['dashboard-changed'],
  data() {
    return {
      companies: [],
      search: '',
      searchBy: 'all',
      status: '',
      loading: false,
      error: '',
    }
  },
  computed: {
    searchPlaceholder() {
      const labels = {
        all: 'Search name, industry, location, email',
        name: 'Search company name',
        industry: 'Search industry',
        location: 'Search location',
        email: 'Search email',
      }

      return labels[this.searchBy]
    },
  },
  mounted() {
    this.loadCompanies()
  },
  methods: {
    headers() {
      return {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      }
    },
    accountStatus(company) {
      if (company.is_blacklisted) return 'Blacklisted'
      if (!company.is_active) return 'Inactive'
      return 'Active'
    },
    async loadCompanies() {
      this.loading = true
      this.error = ''

      try {
        const response = await axios.get('http://127.0.0.1:5000/api/admin/companies', {
          params: {
            search: this.search,
            search_by: this.searchBy,
            status: this.status,
          },
          headers: this.headers(),
        })
        this.companies = response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load companies.'
      } finally {
        this.loading = false
      }
    },
    async approveCompany(id) {
      this.error = ''

      try {
        await axios.patch(`http://127.0.0.1:5000/api/admin/companies/${id}/approve`, {}, {
          headers: this.headers(),
        })
        this.$emit('dashboard-changed')
        this.loadCompanies()
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not approve company.'
      }
    },
    async rejectCompany(id) {
      const reason = window.prompt('Reason for rejection?', '')

      if (reason === null) return

      this.error = ''

      try {
        await axios.patch(`http://127.0.0.1:5000/api/admin/companies/${id}/reject`, { reason }, {
          headers: this.headers(),
        })
        this.$emit('dashboard-changed')
        this.loadCompanies()
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not reject company.'
      }
    },
    async deactivateUser(userId) {
      this.error = ''

      try {
        await axios.patch(`http://127.0.0.1:5000/api/admin/users/${userId}/deactivate`, {}, {
          headers: this.headers(),
        })
        this.$emit('dashboard-changed')
        this.loadCompanies()
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not deactivate account.'
      }
    },
    async blacklistUser(userId) {
      this.error = ''

      try {
        await axios.patch(`http://127.0.0.1:5000/api/admin/users/${userId}/blacklist`, {}, {
          headers: this.headers(),
        })
        this.$emit('dashboard-changed')
        this.loadCompanies()
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not blacklist account.'
      }
    },
    async unblacklistUser(userId) {
      this.error = ''

      try {
        await axios.patch(`http://127.0.0.1:5000/api/admin/users/${userId}/unblacklist`, {}, {
          headers: this.headers(),
        })
        this.$emit('dashboard-changed')
        this.loadCompanies()
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not unblacklist account.'
      }
    },
  },
}
</script>

<style scoped>
.controls { margin: 12px 0; }
</style>
