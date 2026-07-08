<script setup>
import axios from 'axios'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const profile = ref(null)
const errorMessage = ref('')
const isLoading = ref(true)

onMounted(async () => {
  const token = localStorage.getItem('access_token')

  if (!token) {
    await router.push('/student/login')
    return
  }

  try {
    const response = await axios.get('http://127.0.0.1:5000/api/profile', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    profile.value = response.data
  } catch (error) {
    const status = error.response?.status

    if (status === 401 || status === 403 || status === 422) {
      localStorage.clear()
      await router.push('/student/login')
      return
    }

    errorMessage.value = 'Could not load profile.'
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <main class="profile-page">
    <section class="card">
      <h1>My Profile</h1>

      <p v-if="isLoading">Loading profile...</p>

      <p v-else-if="errorMessage" class="error">
        {{ errorMessage }}
      </p>

      <div v-else-if="profile">
        <p><strong>User ID:</strong> {{ profile.id }}</p>
        <p><strong>Email:</strong> {{ profile.email }}</p>
        <p><strong>Role:</strong> {{ profile.role }}</p>
      </div>
    </section>
  </main>
</template>

<style scoped>
.profile-page {
  padding: 32px;
}

.card {
  max-width: 520px;
  padding: 24px;
  border-radius: 12px;
  background: white;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}

.error {
  color: #b42318;
}
</style>
