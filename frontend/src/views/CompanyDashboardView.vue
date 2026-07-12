<script setup>
import DashboardOverview from '@/components/DashboardOverview.vue'
const stats = [
  { label: 'Total drives', value: 6, helper: '2 currently active' },
  { label: 'Applications', value: 148, helper: '26 new this week', tone: 'green' },
  { label: 'Shortlisted', value: 32, helper: 'Across active drives', tone: 'amber' },
  { label: 'Interviews', value: 12, helper: 'Next seven days', tone: 'blue' },
]
const items = [
  { title: 'Graduate Software Engineer', meta: '72 applicants · Deadline 12 July', status: 'Approved' },
  { title: 'Data Analyst Intern', meta: '41 applicants · Awaiting institute review', status: 'Pending' },
  { title: 'Product Support Associate', meta: '35 applicants · Closed 1 July', status: 'Closed' },
]
const asideItems = [
  { title: '26 new applications', meta: 'Review candidates for active drives.' },
  { title: 'Interview schedule', meta: 'Six interviews are planned for tomorrow.' },
  { title: 'Drive awaiting approval', meta: 'Data Analyst Intern is under review.' },
]
</script>
<template><DashboardOverview role="company" user-name="Nova Labs" greeting="Welcome back, Nova Labs" intro="Review your recruitment activity and candidate pipeline." :stats="stats" section-title="Placement drives" :items="items" aside-title="Activity" :aside-items="asideItems" /></template>
