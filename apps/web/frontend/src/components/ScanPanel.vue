<script setup lang="ts">
import { api, type CommonPlan, type ScanItem } from '../api'
import { ref, watch } from 'vue'

const props = defineProps<{ rootPath: string }>()

const root = ref(props.rootPath)
const result = ref<CommonPlan | null>(null)
const loading = ref(false)
const error = ref('')

watch(
  () => props.rootPath,
  (val) => {
    root.value = val
  },
)

async function doScan() {
  if (!root.value.trim()) return
  loading.value = true
  error.value = ''
  try {
    result.value = await api.scan(root.value.trim())
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to scan'
  } finally {
    loading.value = false
  }
}

function rawCount(items: ScanItem[]) {
  return items.filter((i) => i.role === 'raw').length
}
function sidecarCount(items: ScanItem[]) {
  return items.filter((i) => i.role === 'sidecar').length
}
function otherCount(items: ScanItem[]) {
  return items.filter((i) => i.role === 'other').length
}
</script>

<template>
  <div class="panel">
    <h2>Scan Directory</h2>

    <div class="form-row">
      <div class="form-group">
        <label>Directory Path</label>
        <input v-model="root" type="text" placeholder="/path/to/photos" @keyup.enter="doScan()" />
      </div>
      <button class="btn btn-primary" :disabled="loading || !root.trim()" @click="doScan()">
        {{ loading ? 'Scanning...' : 'Scan' }}
      </button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div v-if="result" class="result-section">
      <div class="summary">
        <div class="summary-item">
          <span class="summary-value">{{ result.items.length }}</span>
          <span class="summary-label">Total Files</span>
        </div>
        <div class="summary-item">
          <span class="summary-value">{{ rawCount(result.items as ScanItem[]) }}</span>
          <span class="summary-label">RAW/DNG</span>
        </div>
        <div class="summary-item">
          <span class="summary-value">{{ sidecarCount(result.items as ScanItem[]) }}</span>
          <span class="summary-label">Sidecars</span>
        </div>
        <div class="summary-item">
          <span class="summary-value">{{ otherCount(result.items as ScanItem[]) }}</span>
          <span class="summary-label">Other</span>
        </div>
      </div>

      <div v-if="result.warnings.length > 0">
        <div v-for="w in result.warnings" :key="w.code" class="alert alert-warning">
          <strong>{{ w.code }}</strong>: {{ w.message }}
          <span v-if="w.path" class="mono"> ({{ w.path }})</span>
        </div>
      </div>

      <div v-if="result.errors.length > 0">
        <div v-for="e in result.errors" :key="e.code" class="alert alert-error">
          <strong>{{ e.code }}</strong>: {{ e.message }}
          <span v-if="e.path" class="mono"> ({{ e.path }})</span>
        </div>
      </div>

      <table v-if="result.items.length > 0">
        <thead>
          <tr>
            <th>Path</th>
            <th>Role</th>
            <th>Extension</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, idx) in (result.items as ScanItem[])" :key="idx">
            <td class="mono">{{ item.path }}</td>
            <td>
              <span :class="['badge', `badge-${item.role}`]">{{ item.role }}</span>
            </td>
            <td class="mono">{{ item.extension }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
