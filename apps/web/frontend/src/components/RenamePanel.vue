<script setup lang="ts">
import { api, type RenamePlan } from '../api'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const props = defineProps<{ rootPath: string }>()

const root = ref(props.rootPath)
const template = ref('')
const templateInput = ref<HTMLInputElement | null>(null)
const strict = ref(false)
const plan = ref<RenamePlan | null>(null)
const loading = ref(false)
const executing = ref(false)
const error = ref('')
const plannedSignature = ref('')
const showConfirm = ref(false)

const currentSignature = computed(() =>
  JSON.stringify({
    root: root.value.trim(),
    template: template.value.trim(),
    strict: strict.value,
  }),
)

const isPlanCurrent = computed(() => !!plan.value && plannedSignature.value === currentSignature.value)
const canExecute = computed(
  () => isPlanCurrent.value && !!plan.value && plan.value.errors.length === 0 && plan.value.items.length > 0,
)
const rawCount = computed(() => plan.value?.items.filter((item) => item.role === 'raw').length ?? 0)
const sidecarCount = computed(
  () => plan.value?.items.filter((item) => item.role === 'sidecar').length ?? 0,
)
const executionCompleted = computed(() => !!plan.value && !plan.value.dry_run && plan.value.errors.length === 0)

const placeholderTokens = [
  { token: '{date:YYYYMMDD}', labelKey: 'rename.placeholderDate', descriptionKey: 'rename.placeholderDateDesc' },
  { token: '{title}', labelKey: 'rename.placeholderTitle', descriptionKey: 'rename.placeholderTitleDesc' },
  { token: '{date:HHMMSS}', labelKey: 'rename.placeholderTime', descriptionKey: 'rename.placeholderTimeDesc' },
  { token: '{original}', labelKey: 'rename.placeholderOriginal', descriptionKey: 'rename.placeholderOriginalDesc' },
]

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
  showConfirm.value = false
  try {
    plan.value = await api.renamePlan(root.value.trim(), template.value || undefined, strict.value)
    plannedSignature.value = currentSignature.value
  } catch {
    error.value = t('common.errorGeneratePlan')
  } finally {
    loading.value = false
  }
}

async function execute() {
  if (!canExecute.value) return
  executing.value = true
  error.value = ''
  showConfirm.value = false
  try {
    plan.value = await api.renameExecute(
      root.value.trim(),
      template.value || undefined,
      strict.value,
    )
    plannedSignature.value = currentSignature.value
  } catch {
    error.value = t('common.errorExecute')
  } finally {
    executing.value = false
  }
}

function confirmAndExecute() {
  showConfirm.value = true
}

function basename(path: string) {
  return path.split(/[\\/]/).pop() || path
}

function dirname(path: string) {
  const parts = path.split(/[\\/]/)
  parts.pop()
  return parts.join('/')
}

function insertPlaceholder(token: string) {
  const input = templateInput.value
  const current = template.value || ''
  if (!input) {
    template.value = `${current}${token}`
    return
  }
  const start = input.selectionStart ?? current.length
  const end = input.selectionEnd ?? current.length
  template.value = `${current.slice(0, start)}${token}${current.slice(end)}`
  requestAnimationFrame(() => {
    input.focus()
    const position = start + token.length
    input.setSelectionRange(position, position)
  })
}

function useDefaultTemplate() {
  template.value = '{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}'
  templateInput.value?.focus()
}
</script>

<template>
  <div class="panel">
    <h2>{{ t('rename.title') }}</h2>

    <section class="stage-guide">
      <div>
        <span class="eyebrow">{{ t('rename.guideEyebrow') }}</span>
        <h3>{{ t('rename.guideTitle') }}</h3>
        <p>{{ t('rename.guideBody') }}</p>
      </div>
      <div class="guide-points">
        <span>{{ t('rename.rawPoint') }}</span>
        <span>{{ t('rename.sidecarPoint') }}</span>
        <span>{{ t('rename.metadataPoint') }}</span>
      </div>
    </section>

    <section class="rename-workbench">
      <div class="template-builder">
        <div class="form-group path-field">
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
          <div class="template-input-row">
            <input
              ref="templateInput"
              v-model="template"
              type="text"
              :placeholder="t('rename.templatePlaceholder')"
            />
            <button class="btn btn-secondary" type="button" @click="useDefaultTemplate">
              {{ t('rename.useDefaultTemplate') }}
            </button>
          </div>
        </div>

        <div class="placeholder-panel">
          <div class="placeholder-heading">
            <strong>{{ t('rename.placeholderTitleText') }}</strong>
            <span>{{ t('rename.placeholderHint') }}</span>
          </div>
          <div class="placeholder-grid">
            <button
              v-for="item in placeholderTokens"
              :key="item.token"
              class="placeholder-chip"
              type="button"
              @click="insertPlaceholder(item.token)"
            >
              <span>{{ t(item.labelKey) }}</span>
              <code>{{ item.token }}</code>
              <small>{{ t(item.descriptionKey) }}</small>
            </button>
          </div>
        </div>

        <label class="strict-toggle">
          <input v-model="strict" type="checkbox" />
          <span>
            <strong>{{ t('rename.strictMode') }}</strong>
            <small>{{ t('rename.strictModeHint') }}</small>
          </span>
        </label>
      </div>

      <aside class="raw-explainer">
        <span class="eyebrow">{{ t('rename.rawInfoEyebrow') }}</span>
        <h3>{{ t('rename.rawInfoTitle') }}</h3>
        <p>{{ t('rename.rawInfoBody') }}</p>
        <ul>
          <li>{{ t('rename.rawInfoMeta') }}</li>
          <li>{{ t('rename.rawInfoDate') }}</li>
          <li>{{ t('rename.rawInfoSafe') }}</li>
        </ul>
      </aside>
    </section>

    <div class="form-row">
      <button class="btn btn-primary" :disabled="loading || !root.trim()" @click="dryRun()">
        {{ loading ? t('rename.generating') : t('rename.dryRun') }}
      </button>
      <button
        v-if="plan && plan.errors.length === 0 && plan.items.length > 0"
        class="btn btn-danger"
        :disabled="executing || !canExecute"
        @click="confirmAndExecute()"
      >
        {{ executing ? t('rename.executing') : t('rename.execute') }}
      </button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="plan && !isPlanCurrent" class="alert alert-warning">
      {{ t('rename.planStale') }}
    </div>
    <div v-if="executionCompleted" class="result-complete">
      <strong>{{ t('rename.completeTitle') }}</strong>
      <span>{{ t('rename.completeBody') }}</span>
    </div>

    <div v-if="plan" class="result-section">
      <div class="summary">
        <div class="summary-item">
          <span class="summary-value">{{ plan.items.length }}</span>
          <span class="summary-label">{{ t('rename.filesToRename') }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-value">{{ rawCount }}</span>
          <span class="summary-label">{{ t('rename.rawFiles') }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-value">{{ sidecarCount }}</span>
          <span class="summary-label">{{ t('rename.sidecarFiles') }}</span>
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
            <th>{{ t('rename.currentNameHeader') }}</th>
            <th>{{ t('rename.plannedNameHeader') }}</th>
            <th>{{ t('rename.roleHeader') }}</th>
            <th>{{ t('rename.statusHeader') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, idx) in plan.items" :key="idx">
            <td>
              <div class="file-name mono">{{ basename(item.source_path) }}</div>
              <div class="file-dir mono">{{ dirname(item.source_path) }}</div>
            </td>
            <td>
              <div class="file-name mono">{{ basename(item.target_path) }}</div>
              <div class="file-dir mono">{{ dirname(item.target_path) }}</div>
            </td>
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

    <div v-if="showConfirm && plan" class="modal-backdrop" @click.self="showConfirm = false">
      <section class="confirm-modal">
        <div class="modal-header">
          <span class="eyebrow">{{ t('rename.execute') }}</span>
          <h3>{{ t('rename.confirmTitle') }}</h3>
        </div>
        <div class="confirm-grid">
          <div>
            <span>{{ t('rename.filesToRename') }}</span>
            <strong>{{ plan.items.length }}</strong>
          </div>
          <div>
            <span>{{ t('rename.rawFiles') }}</span>
            <strong>{{ rawCount }}</strong>
          </div>
          <div>
            <span>{{ t('rename.sidecarFiles') }}</span>
            <strong>{{ sidecarCount }}</strong>
          </div>
          <div>
            <span>{{ t('rename.metadataDirs') }}</span>
            <strong>{{ plan.metadata_changes.length }}</strong>
          </div>
        </div>
        <p class="confirm-copy">{{ t('rename.confirmBody') }}</p>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showConfirm = false">
            {{ t('common.cancel') }}
          </button>
          <button class="btn btn-danger" :disabled="executing" @click="execute()">
            {{ executing ? t('rename.executing') : t('rename.confirmExecute') }}
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.stage-guide {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(220px, 320px);
  gap: 20px;
  border: 1px solid #c7dfe5;
  border-radius: 8px;
  background: linear-gradient(135deg, #f0fafb 0%, #ffffff 70%);
  padding: 18px;
  margin-bottom: 18px;
}

.stage-guide h3,
.raw-explainer h3 {
  margin: 3px 0 6px;
  font-size: 1.05rem;
}

.stage-guide p,
.raw-explainer p {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.guide-points {
  display: grid;
  gap: 8px;
  align-content: center;
}

.guide-points span {
  border: 1px solid #d6e8ec;
  border-radius: 999px;
  background: #fff;
  color: var(--primary);
  font-size: 0.8125rem;
  font-weight: 600;
  padding: 6px 10px;
}

.rename-workbench {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 290px;
  gap: 18px;
  align-items: start;
  margin-bottom: 16px;
}

.template-builder {
  display: grid;
  gap: 14px;
}

.path-field input {
  width: 100%;
}

.template-input-row {
  display: flex;
  gap: 8px;
}

.template-input-row input {
  flex: 1;
}

.placeholder-panel {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface-subtle);
  padding: 12px;
}

.placeholder-heading {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.placeholder-heading span {
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.placeholder-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.placeholder-chip {
  border: 1px solid var(--border);
  border-radius: 7px;
  background: #fff;
  color: var(--text);
  cursor: pointer;
  padding: 9px 10px;
  text-align: left;
}

.placeholder-chip:hover {
  border-color: #9ccbd5;
  background: #f4fbfc;
}

.placeholder-chip span,
.placeholder-chip code,
.placeholder-chip small {
  display: block;
}

.placeholder-chip span {
  font-weight: 700;
}

.placeholder-chip code {
  color: var(--primary);
  font-size: 0.8125rem;
  margin-top: 2px;
}

.placeholder-chip small {
  color: var(--text-secondary);
  font-size: 0.75rem;
  margin-top: 2px;
}

.strict-toggle {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 12px;
}

.strict-toggle small {
  display: block;
  color: var(--text-secondary);
  font-size: 0.75rem;
  margin-top: 2px;
}

.raw-explainer {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #fff;
  padding: 16px;
}

.raw-explainer ul {
  display: grid;
  gap: 8px;
  margin-top: 12px;
  padding-left: 18px;
  color: var(--text-secondary);
  font-size: 0.8125rem;
}

.result-complete {
  display: flex;
  flex-direction: column;
  gap: 3px;
  border: 1px solid #abefc6;
  border-radius: 8px;
  background: var(--success-bg);
  color: var(--success-text);
  padding: 12px 14px;
  margin-bottom: 12px;
}

.result-complete span {
  font-size: 0.875rem;
}

.file-name {
  color: var(--text);
  font-weight: 600;
}

.file-dir {
  color: var(--text-secondary);
  font-size: 0.75rem;
  margin-top: 2px;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(17, 24, 39, 0.42);
  padding: 20px;
}

.confirm-modal {
  width: min(560px, 100%);
  border-radius: 8px;
  background: var(--surface);
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.28);
  padding: 22px;
}

.modal-header {
  border-bottom: 1px solid var(--border);
  margin-bottom: 16px;
  padding-bottom: 12px;
}

.modal-header h3 {
  font-size: 1.125rem;
  margin-top: 4px;
}

.confirm-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 14px;
}

.confirm-grid div {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 10px 12px;
}

.confirm-grid span {
  display: block;
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.confirm-grid strong {
  display: block;
  font-size: 1.375rem;
}

.confirm-copy {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

@media (max-width: 980px) {
  .stage-guide,
  .rename-workbench {
    grid-template-columns: 1fr;
  }

  .template-input-row {
    flex-direction: column;
  }
}
</style>
