<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { api, type ArchivePlan, type ArchiveNamePlan } from '@/api'
import { useJourney } from '../composables/useJourney'
import { native, isTauri } from '@/platform'

const { t } = useI18n()
const { projectRoot } = useJourney()
const outputDir = ref('')
const overwrite = ref(false)
const namePlan = ref<ArchiveNamePlan | null>(null)
const archivePlan = ref<ArchivePlan | null>(null)
const loadingName = ref(false)
const loading = ref(false)
const executing = ref(false)
const error = ref('')
const copied = ref(false)

async function generateName() {
  if (!projectRoot.value) return
  loadingName.value = true
  error.value = ''
  try {
    namePlan.value = await api.archiveName(projectRoot.value, outputDir.value || undefined)
  } catch {
    error.value = t('common.errorGeneratePlan')
  } finally {
    loadingName.value = false
  }
}

async function dryRun() {
  if (!projectRoot.value) return
  loading.value = true
  error.value = ''
  try {
    archivePlan.value = await api.archivePlan(projectRoot.value, outputDir.value, overwrite.value)
  } catch {
    error.value = t('common.errorGeneratePlan')
  } finally {
    loading.value = false
  }
}

async function execute() {
  if (!projectRoot.value) return
  executing.value = true
  error.value = ''
  try {
    archivePlan.value = await api.archiveExecute(projectRoot.value, outputDir.value, overwrite.value)
  } catch {
    error.value = t('common.errorExecute')
  } finally {
    executing.value = false
  }
}

async function copyName() {
  if (!namePlan.value?.archive_name) return
  await native.copyToClipboard(namePlan.value.archive_name)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

async function confirmAndExecute() {
  if (confirm(t('archive.confirm'))) {
    await execute()
  }
}

function formatBytes(bytes: number): string {
  if (bytes >= 1e9) return `${(bytes / 1e9).toFixed(1)} GB`
  if (bytes >= 1e6) return `${(bytes / 1e6).toFixed(1)} MB`
  if (bytes >= 1e3) return `${(bytes / 1e3).toFixed(1)} KB`
  return `${bytes} B`
}
</script>

<template>
  <section>
    <div class="stage-note">
      <strong>{{ t('archive.guideTitle') }}</strong>
      <span>{{ t('archive.guideBody') }}</span>
    </div>

    <div class="form-row">
      <button class="btn" :disabled="loadingName || !projectRoot" @click="generateName">
        {{ loadingName ? t('archive.generating') : t('archive.previewName') }}
      </button>
    </div>

    <div v-if="namePlan" class="panel-card panel-pad" style="margin-bottom:14px">
      <span class="eyebrow">{{ t('archive.archiveNameGenerated') }}</span>
      <div class="mono" style="font-size:15px;margin-top:6px;font-weight:700">{{ namePlan.archive_name }}</div>
      <div style="display:flex;gap:8px;margin-top:8px">
        <button class="btn" @click="copyName">
          {{ copied ? t('archive.copySuccess') : t('archive.copyArchiveName') }}
        </button>
      </div>
      <p class="caption" style="margin-top:8px">{{ t('archive.useManualCompression') }}</p>
    </div>

    <div class="form-row" style="margin-top:14px">
      <div class="form-group">
        <label>{{ t('archive.outputLabel') }}</label>
        <input v-model="outputDir" class="input" type="text" :placeholder="t('archive.outputPlaceholder')" />
      </div>
      <label style="display:flex;align-items:center;gap:6px;font-size:13px">
        <input v-model="overwrite" type="checkbox" />
        {{ t('archive.overwriteLabel') }}
      </label>
    </div>

    <div class="form-row">
      <button class="btn primary" :disabled="loading || !projectRoot" @click="dryRun">
        {{ t('archive.dryRun') }}
      </button>
      <button
        class="btn danger"
        :disabled="executing || !archivePlan || (archivePlan.errors?.length ?? 0) > 0"
        @click="confirmAndExecute"
      >
        {{ executing ? t('archive.executing') : t('archive.execute') }}
      </button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div v-if="archivePlan" class="result-section">
      <div class="summary-grid">
        <div class="summary-item">
          <div class="summary-value">{{ archivePlan.included_count }}</div>
          <div class="summary-label">{{ t('archive.included') }}</div>
        </div>
        <div class="summary-item">
          <div class="summary-value">{{ archivePlan.excluded_count }}</div>
          <div class="summary-label">{{ t('archive.excluded') }}</div>
        </div>
        <div class="summary-item">
          <div class="summary-value">{{ formatBytes(archivePlan.total_size_bytes) }}</div>
          <div class="summary-label">{{ t('archive.totalSize') }}</div>
        </div>
        <div class="summary-item">
          <div class="summary-value">{{ archivePlan.raw_count }}</div>
          <div class="summary-label">{{ t('archive.rawDng') }}</div>
        </div>
      </div>

      <div v-if="archivePlan.archive_path" class="alert alert-success">
        {{ t('archive.archivePath') }}: <span class="mono">{{ archivePlan.archive_path }}</span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.stage-note {
  display: flex; flex-direction: column; gap: 4px;
  border: 1px solid var(--line); border-radius: var(--radius);
  background: var(--panel-soft); padding: 12px 14px; margin-bottom: 16px;
}
.stage-note strong { font-size: 14px; }
.stage-note span { color: var(--muted); font-size: 13px; }

.form-row { display: flex; gap: 10px; align-items: flex-end; margin-bottom: 14px; flex-wrap: wrap; }
.form-group { display: flex; flex-direction: column; gap: 4px; }
.form-group label { font-size: 12px; color: var(--muted); font-weight: 600; }

.caption { color: var(--muted); font-size: 12px; }
.result-section { margin-top: 20px; }
</style>
