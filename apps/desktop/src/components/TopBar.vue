<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useJourney } from '../composables/useJourney'
import { computed } from 'vue'

const { t } = useI18n()
const { activeStep } = useJourney()

const statusKey = computed(() => {
  const map: Record<string, string> = {
    prepare: 'journey.statusPrepared',
    scan: 'journey.statusScanned',
    naming: 'journey.statusReady',
    execute: 'journey.statusPlanned',
    postprocess: 'journey.statusWaiting',
    archive: 'journey.statusArchived',
  }
  return map[activeStep.value] || 'journey.statusReady'
})
</script>

<template>
  <header class="topbar">
    <div class="brand">
      <span class="brand-mark">PW</span>
      <span>Photograph Workflow</span>
    </div>
    <div class="topbar-actions">
      <span class="status-pill">{{ t(statusKey) }}</span>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--line);
  background: var(--chrome);
  padding: 16px 20px;
}

.brand {
  display: flex;
  gap: 10px;
  align-items: center;
  font-weight: 760;
  font-size: 15px;
}

.brand-mark {
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;
  border-radius: 8px;
  background: var(--accent);
  color: #fff;
  font-size: 13px;
  font-weight: 800;
}

.topbar-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}
</style>
