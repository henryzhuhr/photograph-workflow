<script setup lang="ts">
import { api, type RollbackPlan } from '../api'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const props = defineProps<{ rootPath: string }>()

const photoDir = ref(props.rootPath)
const plan = ref<RollbackPlan | null>(null)
const loading = ref(false)
const executing = ref(false)
const error = ref('')

watch(
  () => props.rootPath,
  (val) => {
    photoDir.value = val
  },
)

async function dryRun() {
  if (!photoDir.value.trim()) return
  loading.value = true
  error.value = ''
  try {
    plan.value = await api.rollbackPlan(photoDir.value.trim())
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
    plan.value = await api.rollbackExecute(photoDir.value.trim())
  } catch {
    error.value = t('common.errorExecute')
  } finally {
    executing.value = false
  }
}

function confirmAndExecute() {
  if (window.confirm(t('rollback.confirm'))) {
    execute()
  }
}
</script>

<template>
  <div class="panel">
    <h2>{{ t('rollback.title') }}</h2>
    <p style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 16px">
      {{ t('rollback.description') }}
    </p>

    <div class="form-row">
      <div class="form-group">
        <label>{{ t('rollback.pathLabel') }}</label>
        <input
          v-model="photoDir"
          type="text"
          :placeholder="t('rollback.pathPlaceholder')"
          @keyup.enter="dryRun()"
        />
      </div>
    </div>

    <div class="form-row">
      <button class="btn btn-primary" :disabled="loading || !photoDir.trim()" @click="dryRun()">
        {{ loading ? t('rollback.generating') : t('rollback.dryRun') }}
      </button>
      <button
        v-if="plan && plan.errors.length === 0 && plan.items.length > 0"
        class="btn btn-danger"
        :disabled="executing"
        @click="confirmAndExecute()"
      >
        {{ executing ? t('rollback.executing') : t('rollback.execute') }}
      </button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div v-if="plan" class="result-section">
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

      <div v-if="plan.items.length === 0" class="empty-state">{{ t('rollback.empty') }}</div>

      <table v-else>
        <thead>
          <tr>
            <th>{{ t('rollback.currentHeader') }}</th>
            <th>{{ t('rollback.restoreHeader') }}</th>
            <th>{{ t('rollback.roleHeader') }}</th>
            <th>{{ t('rollback.statusHeader') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, idx) in plan.items" :key="idx">
            <td class="mono">{{ item.current_path }}</td>
            <td class="mono">{{ item.target_original_path }}</td>
            <td>
              <span :class="['badge', `badge-${item.role}`]">{{ item.role }}</span>
            </td>
            <td>
              <span :class="['badge', `badge-${item.status}`]">{{ item.status }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
