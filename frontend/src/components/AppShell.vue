<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

const props = defineProps({ role: { type: String, required: true }, userName: { type: String, required: true } })
const router = useRouter()
const menuOpen = ref(false)
const menus = {
  student: [
    ['Dashboard', '/student'], ['Placement drives', '/student/drives'],
    ['My applications', '/student/applications'], ['My profile', '/student/profile'],
  ],
  company: [
    ['Dashboard', '/company'], ['Placement drives', '/company/drives'],
    ['Applicants', '/company/applicants'], ['Company profile', '/company/profile'],
  ],
  admin: [
    ['Dashboard', '/admin'], ['Companies', '/admin/companies'], ['Students', '/admin/students'],
    ['Drive approvals', '/admin/drives'], ['Reports', '/admin/reports'],
  ],
}
const currentMenu = computed(() => menus[props.role] ?? [])
const roleLabel = computed(() => props.role.charAt(0).toUpperCase() + props.role.slice(1))

async function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('role')
  localStorage.removeItem('email')
  await router.push(`/${props.role}/login`)
}
</script>

<template>
  <div class="shell">
    <aside class="sidebar" :class="{ 'sidebar--open': menuOpen }">
      <RouterLink class="brand" to="/"><span class="brand__mark">P</span><span><strong>Placement</strong><small>Portal</small></span></RouterLink>
      <p class="sidebar__label">{{ roleLabel }} workspace</p>
      <nav class="sidebar__nav">
        <RouterLink v-for="item in currentMenu" :key="item[1]" :to="item[1]" class="nav-item" @click="menuOpen = false"><span>◇</span>{{ item[0] }}</RouterLink>
      </nav>
      <button class="sidebar__logout" type="button" @click="logout">↪ Log out</button>
    </aside>
    <div class="shell__main">
      <header class="topbar">
        <button class="menu-button" type="button" @click="menuOpen = !menuOpen">☰</button>
        <div class="topbar__actions"><button class="notification" type="button">♢<span>3</span></button><div class="profile"><b>{{ userName.charAt(0) }}</b><span><strong>{{ userName }}</strong><small>{{ roleLabel }}</small></span></div></div>
      </header>
      <main class="shell__content"><slot /></main>
    </div>
    <button v-if="menuOpen" class="backdrop" type="button" @click="menuOpen = false" />
  </div>
</template>

<style scoped>
.sidebar { position: fixed; z-index: 30; inset: 0 auto 0 0; display: flex; width: 260px; flex-direction: column; padding: 26px 18px; color: white; background: var(--navy); }.brand { display: flex; align-items: center; gap: 11px; padding: 0 8px; }.brand__mark { display: grid; width: 38px; height: 38px; place-items: center; border-radius: 11px; background: #3b7bed; font-weight: 850; }.brand strong,.brand small,.profile strong,.profile small { display: block; }.brand small { color: #a9b8cf; font-size: .7rem; letter-spacing: .12em; text-transform: uppercase; }.sidebar__label { margin: 42px 10px 12px; color: #8295b2; font-size: .7rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }.sidebar__nav { display: grid; gap: 5px; }.nav-item { display: flex; align-items: center; gap: 12px; min-height: 46px; padding: 0 13px; border-radius: 10px; color: #c8d3e3; font-size: .9rem; font-weight: 650; }.nav-item:hover,.nav-item.router-link-exact-active { color: white; background: #18335d; }.sidebar__logout { margin-top: auto; padding: 13px; border: 0; color: #aebdd2; background: transparent; cursor: pointer; text-align: left; }.shell__main { min-height: 100vh; margin-left: 260px; }.topbar { display: flex; height: 72px; align-items: center; justify-content: flex-end; padding: 0 34px; border-bottom: 1px solid var(--border); background: white; }.topbar__actions,.profile { display: flex; align-items: center; gap: 12px; }.notification,.menu-button { position: relative; border: 0; background: transparent; color: var(--navy); cursor: pointer; font-size: 1.35rem; }.notification span { position: absolute; top: -4px; right: -7px; display: grid; width: 17px; height: 17px; place-items: center; border-radius: 50%; background: var(--red); color: white; font-size: .62rem; }.profile b { display: grid; width: 38px; height: 38px; place-items: center; border-radius: 50%; color: var(--blue); background: var(--blue-soft); }.profile strong { font-size: .84rem; }.profile small { color: var(--text-muted); font-size: .72rem; }.shell__content { display: grid; gap: 26px; max-width: 1500px; margin: 0 auto; padding: 34px; }.menu-button,.backdrop { display: none; }
@media (max-width: 800px) { .sidebar { transform: translateX(-100%); transition: transform 180ms ease; }.sidebar--open { transform: translateX(0); }.shell__main { margin-left: 0; }.topbar { justify-content: space-between; padding: 0 20px; }.menu-button { display: block; }.shell__content { padding: 24px 18px; }.backdrop { position: fixed; z-index: 20; inset: 0; display: block; border: 0; background: rgb(11 24 48 / 45%); } }
</style>
