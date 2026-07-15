<script setup>
import AppShell from './AppShell.vue'
import StatCard from './StatCard.vue'
import StatusBadge from './StatusBadge.vue'

defineProps({
  role: String,
  userName: String,
  greeting: String,
  intro: String,
  stats: Array,
  sectionTitle: String,
  items: Array,
  asideTitle: String,
  asideItems: Array,
})
</script>

<template>
  <AppShell :role="role" :user-name="userName">
    <header><h1 class="page-heading">{{ greeting }}</h1><p class="page-intro">{{ intro }}</p></header>
    <section class="stats-grid">
      <StatCard v-for="stat in stats" :key="stat.label" v-bind="stat" />
    </section>
    <section class="dashboard-grid">
      <article class="card panel">
        <div class="panel__header"><h2 class="section-heading">{{ sectionTitle }}</h2><a class="text-link" href="#">View all</a></div>
        <ul class="list">
          <li v-for="item in items" :key="item.title" class="list-row"><div><p class="list-row__title">{{ item.title }}</p><p class="list-row__meta">{{ item.meta }}</p></div><StatusBadge :status="item.status" /></li>
        </ul>
      </article>
      <article class="card panel">
        <div class="panel__header"><h2 class="section-heading">{{ asideTitle }}</h2></div>
        <ul class="list">
          <li v-for="item in asideItems" :key="item.title" class="notice"><span>●</span><div><p class="list-row__title">{{ item.title }}</p><p class="list-row__meta">{{ item.meta }}</p></div></li>
        </ul>
      </article>
    </section>
  </AppShell>
</template>

<style scoped>
.notice { display: flex; gap: 12px; padding: 10px 0; }.notice > span { color: var(--blue); font-size: .7rem; }
</style>
