<script setup>
import { RouterLink } from 'vue-router'

defineProps({
  mode: {
    type: String,
    default: 'login',
  },
})
</script>

<template>
  <main class="portal-choice">
    <RouterLink class="portal-choice__logo" to="/"><b>P</b> Placement Portal</RouterLink>
    <section class="portal-choice__heading">
      <span>{{ mode === 'login' ? 'Welcome back' : 'Create your account' }}</span>
      <h1>Who are you?</h1>
      <p>Choose your portal to {{ mode === 'login' ? 'sign in' : 'register' }}.</p>
    </section>
    <section class="portal-cards">
      <RouterLink class="portal-card card" :to="`/student/${mode}`">
        <div class="portal-card__icon">S</div><h2>I am a Student</h2>
        <p>Explore placement drives and manage your applications.</p><strong>Continue as student →</strong>
      </RouterLink>
      <RouterLink class="portal-card card" :to="`/company/${mode}`">
        <div class="portal-card__icon portal-card__icon--company">C</div><h2>I am a Company</h2>
        <p>Post opportunities and connect with eligible students.</p><strong>Continue as company →</strong>
      </RouterLink>
    </section>
    <p class="portal-choice__switch">
      {{ mode === 'login' ? "Don't have an account?" : 'Already have an account?' }}
      <RouterLink :to="mode === 'login' ? '/register' : '/login'">{{ mode === 'login' ? 'Register' : 'Sign in' }}</RouterLink>
    </p>
  </main>
</template>

<style scoped>
.portal-choice { display: grid; min-height: 100vh; align-content: center; justify-items: center; gap: 32px; padding: 40px 24px; background: #f6f8fc; }
.portal-choice__logo { position: absolute; top: 28px; left: 32px; display: flex; align-items: center; gap: 10px; font-weight: 800; }
.portal-choice__logo b { display: grid; width: 36px; height: 36px; place-items: center; border-radius: 10px; color: white; background: var(--blue); }
.portal-choice__heading { text-align: center; }.portal-choice__heading span { color: var(--blue); font-size: .75rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.portal-choice__heading h1 { margin: 10px 0; font-size: clamp(2.3rem, 5vw, 3.7rem); }.portal-choice__heading p,.portal-card p,.portal-choice__switch { color: var(--text-muted); }
.portal-cards { display: grid; width: min(820px, 100%); grid-template-columns: repeat(2, 1fr); gap: 20px; }.portal-card { padding: 30px; transition: transform 160ms ease, border-color 160ms ease; }
.portal-card:hover { border-color: var(--blue); transform: translateY(-4px); }.portal-card__icon { display: grid; width: 48px; height: 48px; place-items: center; border-radius: 13px; color: var(--blue); background: var(--blue-soft); font-weight: 850; }
.portal-card__icon--company { color: var(--green); background: var(--green-soft); }.portal-card h2 { margin: 22px 0 8px; }.portal-card strong,.portal-choice__switch a { color: var(--blue); }.portal-choice__switch { margin: 0; }
@media (max-width: 650px) { .portal-cards { grid-template-columns: 1fr; }.portal-choice__logo { position: static; justify-self: start; width: min(820px, 100%); } }
</style>
