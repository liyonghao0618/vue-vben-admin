<script lang="ts" setup>
interface PortalPageSection {
  description: string;
  title: string;
}

defineProps<{
  accent: string;
  description: string;
  heroStats: PortalPageSection[];
  role: string;
  sections: PortalPageSection[];
  title: string;
}>();
</script>

<template>
  <div class="portal-page" :style="{ '--portal-accent': accent }">
    <section class="hero-card">
      <p class="eyebrow">{{ role }}</p>
      <h1>{{ title }}</h1>
      <p class="summary">{{ description }}</p>
      <div class="stats-grid">
        <article v-for="item in heroStats" :key="item.title" class="data-card">
          <h2>{{ item.title }}</h2>
          <p>{{ item.description }}</p>
        </article>
      </div>
    </section>

    <section class="section-grid">
      <article v-for="item in sections" :key="item.title" class="section-card">
        <h3>{{ item.title }}</h3>
        <p>{{ item.description }}</p>
      </article>
    </section>
  </div>
</template>

<style scoped>
.portal-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, color-mix(in srgb, var(--portal-accent) 16%, transparent), transparent 32%),
    linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
}

.hero-card,
.section-card {
  border: 1px solid color-mix(in srgb, var(--portal-accent) 18%, #dbeafe);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
}

.hero-card {
  padding: 32px;
}

.eyebrow {
  margin: 0 0 12px;
  color: var(--portal-accent);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  color: #0f172a;
  font-size: 32px;
  line-height: 1.2;
}

.summary {
  max-width: 760px;
  margin: 16px 0 0;
  color: #334155;
  font-size: 16px;
  line-height: 1.8;
}

.stats-grid,
.section-grid {
  display: grid;
  gap: 16px;
  margin-top: 24px;
}

.stats-grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.section-grid {
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.data-card,
.section-card {
  padding: 20px;
}

h2,
h3 {
  margin: 0;
  color: #0f172a;
}

.data-card p,
.section-card p {
  margin: 10px 0 0;
  color: #475569;
  line-height: 1.7;
}

@media (max-width: 768px) {
  .portal-page {
    padding: 16px;
  }

  .hero-card {
    padding: 24px;
  }

  h1 {
    font-size: 26px;
  }
}
</style>
