<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useJourney } from '../composables/useJourney'
import { computed } from 'vue'

const { t } = useI18n()
const { activeStep, scanResult, renamePlan, projectRoot } = useJourney()

const rawCount = computed(() => {
  if (!scanResult.value?.items) return 0
  return scanResult.value.items.filter((i: any) => i.role === 'raw').length
})

const sidecarCount = computed(() => {
  if (!scanResult.value?.items) return 0
  return scanResult.value.items.filter((i: any) => i.role === 'sidecar').length
})

const otherCount = computed(() => {
  if (!scanResult.value?.items) return 0
  return scanResult.value.items.filter((i: any) => i.role === 'other').length
})

const errorCount = computed(() => {
  return scanResult.value?.errors?.length ?? 0
})

const nextAction = computed(() => {
  const map: Record<string, string> = {
    prepare: 'projectBar.chooseDirectory',
    scan: 'naming.generatePlan',
    naming: 'naming.generatePlan',
    execute: 'execute.executeRename',
    postprocess: 'postprocess.markDone',
    archive: 'archive.execute',
  }
  return map[activeStep.value] || 'naming.generatePlan'
})

const nextHint = computed(() => {
  const map: Record<string, string> = {
    prepare: 'prepare.guideBody',
    scan: 'scan.guideBody',
    naming: 'execute.guideTitle',
    execute: 'execute.confirmBody',
    postprocess: 'postprocess.reminder',
    archive: 'archive.guideBody',
  }
  return map[activeStep.value] || ''
})

const isWrite = computed(() => activeStep.value === 'execute' || activeStep.value === 'archive')
</script>

<template>
  <aside class="inspector">
    <h4>{{ t('inspector.projectSummary') }}</h4>
    <div class="inspector-card">
      <div class="inspector-grid">
        <div class="mini-stat">
          <strong>—</strong>
          <span>{{ t('inspector.photoDirs') }}</span>
        </div>
        <div class="mini-stat">
          <strong>{{ rawCount }}</strong>
          <span>{{ t('inspector.rawDng') }}</span>
        </div>
        <div class="mini-stat">
          <strong>{{ sidecarCount }}</strong>
          <span>{{ t('inspector.sidecars') }}</span>
        </div>
        <div class="mini-stat">
          <strong>{{ errorCount }}</strong>
          <span>{{ t('inspector.errors') }}</span>
        </div>
      </div>
    </div>
    <div class="inspector-card next-step">
      <span class="eyebrow">{{ t('inspector.nextStep') }}</span>
      <strong>{{ t(nextAction) }}</strong>
      <p class="caption">{{ t(nextHint) }}</p>
      <span v-if="isWrite" class="pill warn" style="margin-top:8px">写入磁盘</span>
      <span v-else class="pill info" style="margin-top:8px">只读预览</span>
    </div>
    <div class="inspector-card">
      <span class="eyebrow">{{ t('inspector.localAccess') }}</span>
      <p class="caption" v-if="projectRoot">{{ projectRoot }}</p>
      <p class="caption" v-else>{{ t('inspector.localAccessHint') }}</p>
    </div>
  </aside>
</template>

<style scoped>
.inspector {
  background: var(--chrome-soft);
  border-left: 1px solid var(--line);
  padding: 18px;
}

.inspector h4 {
  margin: 0 0 10px;
  font-size: 15px;
}

.inspector-card {
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--panel);
  padding: 12px;
  margin-bottom: 10px;
}

.inspector-card.next-step {
  border-color: var(--accent-line);
  background: var(--accent-soft);
}

.inspector-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.mini-stat {
  border-radius: 10px;
  background: var(--panel-soft);
  padding: 10px;
}

.mini-stat strong {
  display: block;
  font-size: 18px;
}

.mini-stat span {
  color: var(--muted);
  font-size: 11px;
}

.caption {
  margin-top: 6px;
  color: var(--muted);
  font-size: 12px;
}
</style>
