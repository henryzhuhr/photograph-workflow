<script setup lang="ts">
import { api, type ArchivePlan, type ArchiveNamePlan } from '../api'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const props = defineProps<{ rootPath: string }>()

const sourceDir = ref(props.rootPath)
const outputDir = ref('')
const overwrite = ref(false)

const namePlan = ref<ArchiveNamePlan | null>(null)
const archivePlan = ref<ArchivePlan | null>(null)
const loading = ref(false)
const loadingName = ref(false)
const executing = ref(false)
const error = ref('')

watch(
  () => props.rootPath,
  (val) => {
    sourceDir.value = val
  },
)

async function generateName() {
  if (!sourceDir.value.trim()) return
  loadingName.value = true
  error.value = ''
  try {
    namePlan.value = await api.archiveName(
      sourceDir.value.trim(),
      outputDir.value.trim() || undefined,
    )
  } catch {
    error.value = t('common.errorFailed')
  } finally {
    loadingName.value = false
  }
}

async function dryRun() {
  if (!sourceDir.value.trim() || !outputDir.value.trim()) return
  loading.value = true
  error.value = ''
  try {
    archivePlan.value = await api.archivePlan(
      sourceDir.value.trim(),
      outputDir.value.trim(),
      overwrite.value,
    )
  } catch {
    error.value = t('common.errorGeneratePlan')
  } finally {
    loading.value = false
  }
}

async function execute() {
  executing.value = true
  error.value = ''
  try {
    archivePlan.value = await api.archiveExecute(
      sourceDir.value.trim(),
      outputDir.value.trim(),
      overwrite.value,
    )
  } catch {
    error.value = t('common.errorExecute')
  } finally {
    executing.value = false
  }
}

function confirmAndExecute() {
  if (window.confirm(t('archive.confirm'))) {
    execute()
  }
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`
}
</script>

<template>
  <div class="panel">
    <h2>{{ t('archive.title') }}</h2>

    <div class="form-row">
      <div class="form-group">
        <label>{{ t('archive.sourceLabel') }}</label>
        <input v-model="sourceDir" type="text" :placeholder="t('archive.sourcePlaceholder')" />
      </div>
      <div class="form-group">
        <label>{{ t('archive.outputLabel') }}</label>
        <input v-model="outputDir" type="text" :placeholder="t('archive.outputPlaceholder')" />
      </div>
      <div class="form-group">
        <label style="display: flex; align-items: center; gap: 6px">
          <input v-model="overwrite" type="checkbox" />
          {{ t('archive.overwriteLabel') }}
        </label>
      </div>
    </div>

    <div class="form-row">
      <button
        class="btn btn-secondary"
        :disabled="loadingName || !sourceDir.trim()"
        @click="generateName()"
      >
        {{ loadingName ? t('archive.generating') : t('archive.previewName') }}
      </button>
      <button
        class="btn btn-primary"
        :disabled="loading || !sourceDir.trim() || !outputDir.trim()"
        @click="dryRun()"
      >
        {{ loading ? t('archive.generating') : t('archive.dryRun') }}
      </button>
      <button
        v-if="archivePlan && archivePlan.errors.length === 0 && archivePlan.items.length > 0"
        class="btn btn-danger"
        :disabled="executing"
        @click="confirmAndExecute()"
      >
        {{ executing ? t('archive.executing') : t('archive.execute') }}
      </button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <!-- Archive Name Preview -->
    <div v-if="namePlan" class="result-section">
      <h3 style="font-size: 0.9375rem; margin-bottom: 8px">{{ t('archive.nameHeader') }}</h3>
      <div class="alert alert-warning" v-for="w in namePlan.warnings" :key="w.code">
        <strong>{{ w.code }}</strong>: {{ w.message }}
      </div>
      <table>
        <thead>
          <tr>
            <th>Source</th>
            <th>Archive Name</th>
            <th>Archive Path</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="mono">{{ namePlan.source_dir }}</td>
            <td class="mono">{{ namePlan.archive_name }}</td>
            <td class="mono">{{ namePlan.archive_path || t('archive.noOutputDir') }}</td>
            <td class="mono">{{ namePlan.archived_at }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Archive Plan -->
    <div v-if="archivePlan" class="result-section">
      <h3 style="font-size: 0.9375rem; margin-bottom: 8px; margin-top: 20px">
        {{ t('archive.planHeader') }}
      </h3>

      <div class="summary">
        <div class="summary-item">
          <span class="summary-value">{{ archivePlan.included_count }}</span>
          <span class="summary-label">{{ t('archive.included') }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-value">{{ archivePlan.excluded_count }}</span>
          <span class="summary-label">{{ t('archive.excluded') }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-value">{{ formatBytes(archivePlan.total_size_bytes) }}</span>
          <span class="summary-label">{{ t('archive.totalSize') }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-value">{{ archivePlan.raw_count }}</span>
          <span class="summary-label">{{ t('archive.rawDng') }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-value">{{ archivePlan.sidecar_count }}</span>
          <span class="summary-label">{{ t('archive.sidecars') }}</span>
        </div>
      </div>

      <div class="mono" style="margin-bottom: 16px; font-size: 0.875rem">
        {{ t('archive.archivePath') }}: <strong>{{ archivePlan.archive_path }}</strong>
      </div>

      <div v-if="archivePlan.warnings.length > 0">
        <div v-for="w in archivePlan.warnings" :key="w.code" class="alert alert-warning">
          <strong>{{ w.code }}</strong>: {{ w.message }}
        </div>
      </div>

      <div v-if="archivePlan.errors.length > 0">
        <div v-for="e in archivePlan.errors" :key="e.code" class="alert alert-error">
          <strong>{{ e.code }}</strong>: {{ e.message }}
        </div>
      </div>

      <table v-if="archivePlan.items.length > 0">
        <thead>
          <tr>
            <th>{{ t('archive.sourceHeader') }}</th>
            <th>{{ t('archive.sizeHeader') }}</th>
            <th>{{ t('archive.includedHeader') }}</th>
            <th>{{ t('archive.excludeReasonHeader') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, idx) in archivePlan.items" :key="idx">
            <td class="mono">{{ item.source_path }}</td>
            <td class="mono">{{ item.size_bytes ? formatBytes(item.size_bytes) : '-' }}</td>
            <td>
              <span :class="['badge', item.included ? 'badge-renamed' : 'badge-other']">
                {{ item.included ? t('archive.yes') : t('archive.no') }}
              </span>
            </td>
            <td>{{ item.exclude_reason || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
