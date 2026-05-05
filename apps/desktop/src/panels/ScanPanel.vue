<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { api } from '@/api'
import { useJourney } from '../composables/useJourney'

const { t } = useI18n()
const { projectRoot, scanResult } = useJourney()
const loading = ref(false)
const error = ref('')

const result = computed(() => scanResult.value)

const rawCount = computed(() => result.value?.items?.filter((i: any) => i.role === 'raw').length ?? 0)
const sidecarCount = computed(() => result.value?.items?.filter((i: any) => i.role === 'sidecar').length ?? 0)
const otherCount = computed(() => result.value?.items?.filter((i: any) => i.role === 'other').length ?? 0)
const totalCount = computed(() => result.value?.items?.length ?? 0)
const errors = computed(() => result.value?.errors ?? [])
const warnings = computed(() => result.value?.warnings ?? [])

async function doScan() {
  if (!projectRoot.value) return
  loading.value = true
  error.value = ''
  try {
    scanResult.value = await api.scan(projectRoot.value)
  } catch {
    error.value = t('common.errorScan')
  } finally {
    loading.value = false
  }
}

watch(projectRoot, (val) => {
  if (val) {
    scanResult.value = null
  }
})
</script>

<template>
  <section>
    <div class="stage-note">
      <strong>{{ t('scan.guideTitle') }}</strong>
      <span>{{ t('scan.guideBody') }}</span>
    </div>

    <div class="form-row">
      <button class="btn primary" :disabled="loading || !projectRoot" @click="doScan">
        {{ loading ? t('scan.scanning') : t('scan.scan') }}
      </button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div v-if="result" class="result-section">
      <div class="summary-grid">
        <div class="summary-item">
          <div class="summary-value">{{ totalCount }}</div>
          <div class="summary-label">{{ t('scan.totalFiles') }}</div>
        </div>
        <div class="summary-item">
          <div class="summary-value">{{ rawCount }}</div>
          <div class="summary-label">{{ t('scan.rawDng') }}</div>
        </div>
        <div class="summary-item">
          <div class="summary-value">{{ sidecarCount }}</div>
          <div class="summary-label">{{ t('scan.sidecars') }}</div>
        </div>
        <div class="summary-item">
          <div class="summary-value">{{ otherCount }}</div>
          <div class="summary-label">{{ t('scan.other') }}</div>
        </div>
      </div>

      <div v-if="errors.length > 0" class="alert alert-error">
        <div v-for="(e, i) in errors" :key="i">{{ e.code }}: {{ e.message }}</div>
      </div>
      <div v-if="warnings.length > 0" class="alert alert-warning">
        <div v-for="(w, i) in warnings" :key="i">{{ w.code }}: {{ w.message }}</div>
      </div>

      <div v-if="result.items && result.items.length > 0" class="panel-card" style="overflow:hidden">
        <table>
          <thead>
            <tr>
              <th>Path</th>
              <th>Role</th>
              <th>Extension</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in result.items" :key="item.path">
              <td class="mono">{{ item.path }}</td>
              <td><span :class="['pill', item.role === 'raw' ? 'info' : item.role === 'sidecar' ? 'ready' : '']">{{ item.role }}</span></td>
              <td>{{ item.extension }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<style scoped>
.stage-note {
  display: flex;
  flex-direction: column;
  gap: 4px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--panel-soft);
  padding: 12px 14px;
  margin-bottom: 16px;
}
.stage-note strong { font-size: 14px; }
.stage-note span { color: var(--muted); font-size: 13px; }
.form-row { display: flex; gap: 8px; margin-bottom: 16px; }
.result-section { margin-top: 20px; }
</style>
