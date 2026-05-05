<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useJourney, type JourneyStep } from '../composables/useJourney'
import { computed } from 'vue'

const { t } = useI18n()
const { activeStep, utilityPage, goToStep, openUtility, closeUtility } = useJourney()

interface StepDef {
  id: JourneyStep
  label: string
  desc: string
}

const steps: StepDef[] = [
  { id: 'prepare', label: 'journey.prepare', desc: 'journey.prepareDesc' },
  { id: 'scan', label: 'journey.scan', desc: 'journey.scanDesc' },
  { id: 'naming', label: 'journey.naming', desc: 'journey.namingDesc' },
  { id: 'execute', label: 'journey.execute', desc: 'journey.executeDesc' },
  { id: 'postprocess', label: 'journey.postprocess', desc: 'journey.postprocessDesc' },
  { id: 'archive', label: 'journey.archive', desc: 'journey.archiveDesc' },
]

const currentIndex = computed(() => steps.findIndex((s) => s.id === activeStep.value))

function isDone(idx: number) {
  return idx < currentIndex.value
}

function isActive(id: JourneyStep) {
  return activeStep.value === id && !utilityPage.value
}

function handleStep(id: JourneyStep) {
  closeUtility()
  goToStep(id)
}

function handleUtility(page: 'settings' | 'safety') {
  if (utilityPage.value === page) {
    closeUtility()
  } else {
    openUtility(page)
  }
}
</script>

<template>
  <aside class="sidebar">
    <span class="eyebrow">{{ t('app.workflow') }}</span>
    <nav class="step-list">
      <button
        v-for="(step, idx) in steps"
        :key="step.id"
        :class="['step', { active: isActive(step.id), done: isDone(idx) }]"
        @click="handleStep(step.id)"
      >
        <span class="step-dot">{{ idx + 1 }}</span>
        <span>
          <strong>{{ t(step.label) }}</strong>
          <span>{{ t(step.desc) }}</span>
        </span>
      </button>
    </nav>
    <div class="utility-link">
      <button
        :class="['btn', { active: utilityPage === 'settings' }]"
        @click="handleUtility('settings')"
      >
        {{ t('journey.settings') }}
      </button>
      <button
        :class="['btn', { active: utilityPage === 'safety' }]"
        @click="handleUtility('safety')"
      >
        {{ t('journey.safety') }}
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  background: var(--chrome-soft);
  border-right: 1px solid var(--line);
  padding: 18px;
  display: flex;
  flex-direction: column;
}

.step-list {
  display: grid;
  gap: 6px;
  margin-top: 12px;
}

.step {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  gap: 10px;
  align-items: start;
  border: 1px solid transparent;
  border-radius: 12px;
  padding: 10px;
  color: var(--muted);
  background: transparent;
  cursor: pointer;
  text-align: left;
  font: inherit;
}

.step:hover {
  border-color: var(--accent-line);
  background: var(--panel);
}

.step:focus-visible {
  outline: 3px solid var(--accent-line);
  outline-offset: 2px;
}

.step.active {
  border-color: var(--accent-line);
  background: var(--accent-soft);
  color: var(--accent);
}

.step.done {
  color: var(--accent);
}

.step-dot {
  display: grid;
  width: 24px;
  height: 24px;
  place-items: center;
  border: 1px solid currentColor;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
}

.step strong {
  display: block;
  color: currentColor;
  font-size: 14px;
}

.step span:last-child {
  display: block;
  margin-top: 2px;
  font-size: 12px;
}

.utility-link {
  display: grid;
  gap: 8px;
  margin-top: auto;
  border-top: 1px solid var(--line);
  padding-top: 14px;
}

.utility-link .btn {
  width: 100%;
  text-align: left;
}

.utility-link .btn.active {
  border-color: var(--accent-line);
  background: var(--accent-soft);
  color: var(--accent);
}
</style>
