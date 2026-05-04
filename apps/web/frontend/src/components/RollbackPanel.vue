<script setup lang="ts">
import { api, type RollbackPlan } from '../api'
import { ref, watch } from 'vue'

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
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to generate plan'
  } finally {
    loading.value = false
  }
}

async function execute() {
  executing.value = true
  error.value = ''
  try {
    plan.value = await api.rollbackExecute(photoDir.value.trim())
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to execute'
  } finally {
    executing.value = false
  }
}

function confirmAndExecute() {
  if (window.confirm('Execute rollback? This will restore original file names.')) {
    execute()
  }
}
</script>

<template>
  <div class="panel">
    <h2>Rollback</h2>
    <p style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 16px">
      Restore original file names using .metadata.json records.
    </p>

    <div class="form-row">
      <div class="form-group">
        <label>Photo Directory Path</label>
        <input
          v-model="photoDir"
          type="text"
          placeholder="/path/to/photo-directory"
          @keyup.enter="dryRun()"
        />
      </div>
    </div>

    <div class="form-row">
      <button class="btn btn-primary" :disabled="loading || !photoDir.trim()" @click="dryRun()">
        {{ loading ? 'Generating...' : 'Dry Run' }}
      </button>
      <button
        v-if="plan && plan.errors.length === 0 && plan.items.length > 0"
        class="btn btn-danger"
        :disabled="executing"
        @click="confirmAndExecute()"
      >
        {{ executing ? 'Executing...' : 'Execute Rollback' }}
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

      <div v-if="plan.items.length === 0" class="empty-state">No files to rollback.</div>

      <table v-else>
        <thead>
          <tr>
            <th>Current</th>
            <th>Restore To</th>
            <th>Role</th>
            <th>Status</th>
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
