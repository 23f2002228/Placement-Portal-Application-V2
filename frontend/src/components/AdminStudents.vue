<template>
  <section>
    <h2>Students</h2>

    <div class="controls">
      <input v-model="search" placeholder="Search name, roll number, phone, email" @keyup.enter="loadStudents" />
      <button @click="loadStudents">Search</button>
    </div>

    <p v-if="loading">Loading students...</p>
    <p v-if="error" class="error">{{ error }}</p>

    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Roll No.</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Branch</th>
          <th>Year</th>
          <th>CGPA</th>
          <th>Account</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="student in students" :key="student.id">
          <td>{{ student.full_name }}</td>
          <td>{{ student.roll_number }}</td>
          <td>{{ student.email }}</td>
          <td>{{ student.phone }}</td>
          <td>{{ student.branch }}</td>
          <td>{{ student.year }}</td>
          <td>{{ student.cgpa }}</td>
          <td>{{ accountStatus(student) }}</td>
          <td class="actions">
            <button @click="activateUser(student.user_id)">Activate</button>
            <button @click="deactivateUser(student.user_id)">Deactivate</button>
            <button @click="blacklistUser(student.user_id)">Blacklist</button>
            <button @click="unblacklistUser(student.user_id)">Unblacklist</button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AdminStudents',
  emits: ['dashboard-changed'],
  data() {
    return {
      students: [],
      search: '',
      loading: false,
      error: '',
    }
  },
  mounted() {
    this.loadStudents()
  },
  methods: {
    headers() {
      return {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      }
    },
    accountStatus(student) {
      if (student.is_blacklisted) return 'Blacklisted'
      if (!student.is_active) return 'Inactive'
      return 'Active'
    },
    async loadStudents() {
      this.loading = true
      this.error = ''

      try {
        const response = await axios.get('http://127.0.0.1:5000/api/admin/students', {
          params: { search: this.search },
          headers: this.headers(),
        })
        this.students = response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load students.'
      } finally {
        this.loading = false
      }
    },
    async activateUser(userId) {
      this.error = ''

      try {
        await axios.patch(`http://127.0.0.1:5000/api/admin/users/${userId}/activate`, {}, {
          headers: this.headers(),
        })
        this.$emit('dashboard-changed')
        this.loadStudents()
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not activate account.'
      }
    },
    async deactivateUser(userId) {
      this.error = ''

      try {
        await axios.patch(`http://127.0.0.1:5000/api/admin/users/${userId}/deactivate`, {}, {
          headers: this.headers(),
        })
        this.$emit('dashboard-changed')
        this.loadStudents()
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
        this.loadStudents()
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
        this.loadStudents()
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
