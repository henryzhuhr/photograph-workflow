<script setup lang="ts">
import { useJourney } from '../composables/useJourney'

const { theme } = useJourney()

const themes = [
  { id: 'cobalt', name: '中性石墨 + 柔和钴蓝' },
  { id: 'cyan', name: '冷调单色 + 青色强调' },
  { id: 'paper', name: '暖纸 + 鼠尾草绿' },
  { id: 'olive', name: '银橄榄' },
  { id: 'darkroom', name: '暗房低光' },
]

function setTheme(id: string) {
  theme.value = id
}
</script>

<template>
  <div class="theme-strip">
    <button
      v-for="t in themes"
      :key="t.id"
      :class="['theme-card', `theme-${t.id}`, { selected: theme === t.id }]"
      :aria-pressed="theme === t.id"
      @click="setTheme(t.id)"
    >
      <strong>{{ t.name }}</strong>
      <span class="theme-dots">
        <span v-for="i in 5" :key="i"></span>
      </span>
    </button>
  </div>
</template>

<style scoped>
.theme-strip {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 2px 0 8px;
}

.theme-card {
  flex: 0 0 260px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: var(--panel-soft);
  color: var(--ink);
  cursor: pointer;
  padding: 12px;
  text-align: left;
  font: inherit;
  transition: border-color 0.16s ease, box-shadow 0.16s ease;
}

.theme-card:hover {
  border-color: var(--accent-line);
  box-shadow: 0 10px 24px rgba(24, 33, 47, 0.1);
}

.theme-card:focus-visible {
  outline: 3px solid var(--accent-line);
  outline-offset: 2px;
}

.theme-card.selected {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px var(--accent-soft), 0 12px 28px rgba(24, 33, 47, 0.12);
}

.theme-card strong {
  display: block;
  font-size: 13px;
}

.theme-dots {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 5px;
  margin-top: 10px;
}

.theme-dots span {
  height: 20px;
  border: 1px solid rgba(24, 33, 47, 0.14);
  border-radius: 999px;
}

.theme-cobalt .theme-dots span:nth-child(1) { background: #f5f6f8; }
.theme-cobalt .theme-dots span:nth-child(2) { background: #ffffff; }
.theme-cobalt .theme-dots span:nth-child(3) { background: #3a63d8; }
.theme-cobalt .theme-dots span:nth-child(4) { background: #16865a; }
.theme-cobalt .theme-dots span:nth-child(5) { background: #a66300; }

.theme-cyan .theme-dots span:nth-child(1) { background: #f2f7f8; }
.theme-cyan .theme-dots span:nth-child(2) { background: #ffffff; }
.theme-cyan .theme-dots span:nth-child(3) { background: #0f7285; }
.theme-cyan .theme-dots span:nth-child(4) { background: #127450; }
.theme-cyan .theme-dots span:nth-child(5) { background: #9b610f; }

.theme-paper .theme-dots span:nth-child(1) { background: #f7f4ed; }
.theme-paper .theme-dots span:nth-child(2) { background: #fffdf8; }
.theme-paper .theme-dots span:nth-child(3) { background: #4f6f52; }
.theme-paper .theme-dots span:nth-child(4) { background: #3f7a4b; }
.theme-paper .theme-dots span:nth-child(5) { background: #9a6500; }

.theme-olive .theme-dots span:nth-child(1) { background: #f3f5f2; }
.theme-olive .theme-dots span:nth-child(2) { background: #ffffff; }
.theme-olive .theme-dots span:nth-child(3) { background: #557245; }
.theme-olive .theme-dots span:nth-child(4) { background: #20714f; }
.theme-olive .theme-dots span:nth-child(5) { background: #99640e; }

.theme-darkroom .theme-dots span:nth-child(1) { background: #15171b; }
.theme-darkroom .theme-dots span:nth-child(2) { background: #20242b; }
.theme-darkroom .theme-dots span:nth-child(3) { background: #7ba7ff; }
.theme-darkroom .theme-dots span:nth-child(4) { background: #6fd39a; }
.theme-darkroom .theme-dots span:nth-child(5) { background: #e5ae57; }
</style>
