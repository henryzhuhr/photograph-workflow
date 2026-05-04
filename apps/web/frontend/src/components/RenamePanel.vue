<script setup lang="ts">
import { api, type RenamePlan } from '../api'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const props = defineProps<{ rootPath: string }>()

const root = ref(props.rootPath)
const template = ref('')
const strict = ref(false)
const plan = ref<RenamePlan | null>(null)
const loading = ref(false)
const executing = ref(false)
const error = ref('')

watch(
  () => props.rootPath,
  (val) => {
    root.value = val
  },
)

async function dryRun() {
  if (!root.value.trim()) return
  loading.value = true
  error.value = ''
  try {
    plan.value = await api.renamePlan(root.value.trim(), template.value || undefined, strict.value)
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
    plan.value = await api.renameExecute(
      root.value.trim(),
      template.value || undefined,
      strict.value,
    )
  } catch {
    error.value = t('common.errorExecute')
  } finally {
    executing.value = false
  }
}

function confirmAndExecute() {
  if (window.confirm(t('rename.confirm'))) {
    execute()
  }
}
</script>

<template>
  <div class="panel">
    <h2>{{ t('rename.title') }}</h2>

    <div class="form-row">
      <div class="form-group">
        <label>{{ t('rename.pathLabel') }}</label>
        <input
          v-model="root"
          type="text"
          :placeholder="t('rename.pathPlaceholder')"
          @keyup.enter="dryRun()"
        />
      </div>
      <div class="form-group">
        <label>{{ t('rename.templateLabel') }}</label>
        <input
          v-model="template"
          type="text"
          :placeholder="t('rename.templatePlaceholder')"
        />
      </div>
      <div class="form-group">
        <label style="display: flex; align-items: center; gap: 6px">
          <input v-model="strict" type="checkbox" />
          {{ t('rename.strictMode') }}
        </label>
      </div>
    </div>

    <div class="form-row">
      <button class="btn btn-primary" :disabled="loading || !root.trim()" @click="dryRun()">
        {{ loading ? t('rename.generating') : t('rename.dryRun') }}
      </button>
      <button
        v-if="plan && plan.errors.length === 0 && plan.items.length > 0"
        class="btn btn-danger"
        :disabled="executing"
        @click="confirmAndExecute()"
      >
        {{ executing ? t('rename.executing') : t('rename.execute') }}
      </button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div v-if="plan" class="result-section">
      <div class="summary">
        <div class="summary-item">
          <span class="summary-value">{{ plan.items.length }}</span>
          <span class="summary-label">{{ t('rename.filesToRename') }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-value">{{ plan.metadata_changes.length }}</span>
          <span class="summary-label">{{ t('rename.metadataDirs') }}</span>
        </div>
      </div>

      <div v-if="plan.warnings.length > 0">
        <div v-for="w in plan.warnings" :key="w.code" class="alert alert-warning">
          <strong>{{ w.code }}</strong>: {{ w.message }}
          <span v-if="w.path" class="mono"> ({{ w.path }})</span>
        </div>
      </div>

      <div v-if="plan.errors.length > 0">
        <div v-for="e in plan.errors" :key="e.code" class="alert alert-error">
          <strong>{{ e.code }}</strong>: {{ e.message }}
          <span v-if="e.path" class="mono"> ({{ e.path }})</span>
        </div>
      </div>

      <table v-if="plan.items.length > 0">
        <thead>
          <tr>
            <th>{{ t('rename.sourceHeader') }}</th>
            <th>{{ t('rename.targetHeader') }}</th>
            <th>{{ t('rename.roleHeader') }}</th>
            <th>{{ t('rename.statusHeader') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, idx) in plan.items" :key="idx">
            <td class="mono">{{ item.source_path }}</td>
            <td class="mono">{{ item.target_path }}</td>
            <td>
              <span :class="['badge', `badge-${item.role}`]">{{ item.role }}</span>
            </td>
            <td>
              <span :class="['badge', `badge-${item.status}`]">{{ item.status }}</span>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="empty-state">{{ t('rename.empty') }}</div>
    </div>
  </div>
</template>
