<script setup lang="ts">
import { api, type RenamePlan } from '../api'
import { ref } from 'vue'

const root = ref('')
const template = ref('')
const strict = ref(false)
const plan = ref<RenamePlan | null>(null)
const loading = ref(false)
const executing = ref(false)
const error = ref('')

async function dryRun() {
  if (!root.value.trim()) return
  loading.value = true
  error.value = ''
  try {
    plan.value = await api.renamePlan(root.value.trim(), template.value || undefined, strict.value)
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
    plan.value = await api.renameExecute(
      root.value.trim(),
      template.value || undefined,
      strict.value,
    )
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to execute'
  } finally {
    executing.value = false
  }
}

function confirmAndExecute() {
  if (window.confirm('Execute rename? This will modify files on disk.')) {
    execute()
  }
}
</script>

<template>
  <div class="panel">
    <h2>Rename Files</h2>

    <div class="form-row">
      <div class="form-group">
        <label>Directory Path</label>
        <input v-model="root" type="text" placeholder="/path/to/photos" @keyup.enter="dryRun()" />
      </div>
      <div class="form-group">
        <label>Template (optional)</label>
        <input
          v-model="template"
          type="text"
          placeholder="{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}"
        />
      </div>
      <div class="form-group">
        <label style="display: flex; align-items: center; gap: 6px">
          <input v-model="strict" type="checkbox" />
          Strict mode
        </label>
      </div>
    </div>

    <div class="form-row">
      <button class="btn btn-primary" :disabled="loading || !root.trim()" @click="dryRun()">
        {{ loading ? 'Generating...' : 'Dry Run' }}
      </button>
      <button
        v-if="plan && plan.errors.length === 0 && plan.items.length > 0"
        class="btn btn-danger"
        :disabled="executing"
        @click="confirmAndExecute()"
      >
        {{ executing ? 'Executing...' : 'Execute Rename' }}
      </button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div v-if="plan" class="result-section">
      <div class="summary">
        <div class="summary-item">
          <span class="summary-value">{{ plan.items.length }}</span>
          <span class="summary-label">Files to Rename</span>
        </div>
        <div class="summary-item">
          <span class="summary-value">{{ plan.metadata_changes.length }}</span>
          <span class="summary-label">Metadata Dirs</span>
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
            <th>Source</th>
            <th>Target</th>
            <th>Role</th>
            <th>Status</th>
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

      <div v-else class="empty-state">No rename items generated.</div>
    </div>
  </div>
</template>
