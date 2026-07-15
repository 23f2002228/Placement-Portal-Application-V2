<template>
  <div class="notifications">
    <button type="button" class="bell-button" @click="togglePanel">
      Notifications
      <span v-if="unreadCount" class="badge">{{ unreadCount }}</span>
    </button>

    <div v-if="isOpen" class="panel">
      <div class="panel-header">
        <h3>Notifications</h3>
        <button v-if="unreadCount" type="button" @click="markAllRead">Mark all read</button>
      </div>

      <p v-if="loading">Loading notifications...</p>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="!loading && notifications.length === 0">No notifications yet.</p>

      <ul v-if="notifications.length">
        <li
          v-for="notification in notifications"
          :key="notification.id"
          :class="{ unread: !notification.is_read }"
        >
          <div>
            <strong>{{ notification.title }}</strong>
            <small>{{ notification.created_at }}</small>
          </div>
          <p>{{ notification.message }}</p>
          <button
            v-if="!notification.is_read"
            type="button"
            @click="markRead(notification.id)"
          >
            Mark read
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'NotificationBell',
  data() {
    return {
      notifications: [],
      unreadCount: 0,
      isOpen: false,
      loading: false,
      error: '',
      pollTimer: null,
    }
  },
  mounted() {
    this.loadNotifications()
    this.pollTimer = window.setInterval(this.loadNotifications, 30000)
  },
  beforeUnmount() {
    if (this.pollTimer) {
      window.clearInterval(this.pollTimer)
    }
  },
  methods: {
    headers() {
      return {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      }
    },
    async loadNotifications() {
      this.loading = this.notifications.length === 0
      this.error = ''

      try {
        const response = await axios.get('http://127.0.0.1:5000/api/notifications', {
          headers: this.headers(),
        })
        this.notifications = response.data.notifications || []
        this.unreadCount = response.data.unread_count || 0
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not load notifications.'
      } finally {
        this.loading = false
      }
    },
    togglePanel() {
      this.isOpen = !this.isOpen
      if (this.isOpen) {
        this.loadNotifications()
      }
    },
    async markRead(notificationId) {
      this.error = ''

      try {
        await axios.patch(
          `http://127.0.0.1:5000/api/notifications/${notificationId}/read`,
          {},
          { headers: this.headers() },
        )
        this.loadNotifications()
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not update notification.'
      }
    },
    async markAllRead() {
      this.error = ''

      try {
        await axios.patch(
          'http://127.0.0.1:5000/api/notifications/read-all',
          {},
          { headers: this.headers() },
        )
        this.loadNotifications()
      } catch (error) {
        this.error = error.response?.data?.message || 'Could not update notifications.'
      }
    },
  },
}
</script>

<style scoped>
.notifications { position: relative; }
.bell-button {
  position: relative;
  padding: 9px 12px;
  border: 1px solid #bbb;
  background: white;
  cursor: pointer;
}
.badge {
  position: absolute;
  top: -8px;
  right: -8px;
  display: grid;
  min-width: 20px;
  height: 20px;
  place-items: center;
  border-radius: 999px;
  background: #b42318;
  color: white;
  font-size: 12px;
  font-weight: 700;
}
.panel {
  position: absolute;
  top: 44px;
  right: 0;
  z-index: 10;
  width: min(360px, 90vw);
  max-height: 420px;
  overflow-y: auto;
  border: 1px solid #ddd;
  background: white;
  padding: 12px;
  box-shadow: 0 12px 32px rgba(16, 24, 40, 0.15);
}
.panel-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 10px;
}
.panel-header h3 { margin: 0; font-size: 1rem; }
.panel-header button,
li button {
  padding: 6px 8px;
  border: 1px solid #bbb;
  background: white;
  cursor: pointer;
}
ul {
  display: grid;
  gap: 8px;
  padding: 0;
  margin: 0;
  list-style: none;
}
li {
  border: 1px solid #eee;
  padding: 10px;
}
li.unread { border-color: #9fc5ff; background: #f5f9ff; }
li div {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}
li strong,
li small { display: block; }
li small { color: #667085; font-size: 0.75rem; }
li p { margin: 6px 0; }
.error { color: #b42318; }
</style>
