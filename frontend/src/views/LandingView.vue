<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="landing">
    <header class="landing__nav">
      <RouterLink class="logo" to="/"><b>P</b><span>Placement Portal</span></RouterLink>
      <nav><a href="#features">Features</a>
        <RouterLink to="/student">Student</RouterLink>
        <RouterLink to="/company">Company</RouterLink>
        <RouterLink class="button" to="/admin">Admin</RouterLink>
      </nav>
    </header>
    <main class="hero">
      <section class="hero__copy"><span class="eyebrow">Institute placement management</span>
        <h1>One place for every placement opportunity.</h1>
        <p>Students discover opportunities, companies find the right candidates, and the institute keeps the entire
          process moving.</p>
        <div class="hero__actions">
          <RouterLink class="button" to="/student">Student portal</RouterLink>
          <RouterLink class="button button--secondary" to="/company">Company portal</RouterLink>
        </div>
      </section>
      <!-- <section class="hero__visual card"><div class="mini-header"><b>Placement overview</b><span>Live</span></div><div class="mini-stats"><article><strong>24</strong><small>Active drives</small></article><article><strong>186</strong><small>Applications</small></article><article><strong>42</strong><small>Selections</small></article></div><div class="progress"><p><span>Placement progress</span><b>72%</b></p><div><span /></div></div></section> -->
    </main>
    <section id="features" class="features">
      <article><span>01</span>
        <h2>For students</h2>
        <p>Discover eligible drives, apply, and follow every status update.</p>
      </article>
      <article><span>02</span>
        <h2>For companies</h2>
        <p>Create drives, review applicants, and manage interview rounds.</p>
      </article>
      <article><span>03</span>
        <h2>For administrators</h2>
        <p>Approve companies and drives while tracking institute outcomes.</p>
      </article>
    </section>
  </div>
</template>

<style scoped>
.landing {
  min-height: 100vh;
  overflow: hidden;
  background: radial-gradient(circle at 85% 15%, #dce9ff 0, transparent 28%), white;
}

.landing__nav {
  display: flex;
  max-width: 1180px;
  height: 76px;
  align-items: center;
  justify-content: space-between;
  margin: auto;
  padding: 0 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 800;
}

.logo b {
  display: grid;
  width: 36px;
  height: 36px;
  place-items: center;
  border-radius: 10px;
  color: white;
  background: var(--blue);
}

.landing__nav nav {
  display: flex;
  align-items: center;
  gap: 24px;
  font-size: .9rem;
  font-weight: 650;
}

.hero {
  display: grid;
  max-width: 1180px;
  min-height: 610px;
  grid-template-columns: 1.05fr .95fr;
  align-items: center;
  gap: 70px;
  margin: auto;
  padding: 70px 24px 90px;
}

.eyebrow {
  color: var(--blue);
  font-size: .75rem;
  font-weight: 800;
  letter-spacing: .12em;
  text-transform: uppercase;
}

.hero h1 {
  max-width: 700px;
  margin: 18px 0;
  font-size: clamp(2.8rem, 6vw, 5rem);
  line-height: 1.02;
  letter-spacing: -.055em;
}

.hero__copy>p {
  max-width: 620px;
  margin: 0;
  color: var(--text-muted);
  font-size: 1.08rem;
}

.hero__actions {
  display: flex;
  gap: 12px;
  margin-top: 30px;
}

.hero__visual {
  padding: 30px;
  transform: rotate(1.5deg);
  box-shadow: 0 28px 70px rgb(16 35 68 / 16%);
}

.mini-header,
.progress p {
  display: flex;
  justify-content: space-between;
}

.mini-header span {
  padding: 4px 9px;
  border-radius: 999px;
  color: var(--green);
  background: var(--green-soft);
  font-size: .7rem;
  font-weight: 800;
}

.mini-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin: 28px 0;
}

.mini-stats article {
  padding: 18px 12px;
  border-radius: 12px;
  background: #f6f8fc;
}

.mini-stats strong,
.mini-stats small {
  display: block;
}

.mini-stats strong {
  font-size: 1.7rem;
}

.mini-stats small,
.progress {
  color: var(--text-muted);
  font-size: .75rem;
}

.progress p b {
  color: var(--navy);
}

.progress>div {
  height: 9px;
  border-radius: 10px;
  background: var(--blue-soft);
}

.progress>div span {
  display: block;
  width: 72%;
  height: 100%;
  border-radius: inherit;
  background: var(--blue);
}

.features {
  display: grid;
  max-width: 1180px;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin: auto;
  padding: 60px 24px 90px;
}

.features article {
  padding: 28px;
  border-top: 1px solid var(--border);
}

.features span {
  color: var(--blue);
  font-weight: 800;
}

.features h2 {
  margin: 12px 0 8px;
  font-size: 1.2rem;
}

.features p {
  margin: 0;
  color: var(--text-muted);
}

@media (max-width: 800px) {
  .landing__nav nav>a:not(.button) {
    display: none;
  }

  .hero {
    grid-template-columns: 1fr;
    gap: 40px;
    padding-top: 50px;
  }

  .features {
    grid-template-columns: 1fr;
  }

  .mini-stats {
    grid-template-columns: 1fr;
  }
}
</style>
