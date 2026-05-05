<script setup lang="ts">
import { api, type WorkspaceEntry } from './api'
import { computed, nextTick, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { setLocale } from './i18n'
import { isTauri, native } from './platform'
import WorkspacePanel from './components/WorkspacePanel.vue'
import ScanPanel from './components/ScanPanel.vue'
import RenamePanel from './components/RenamePanel.vue'
import RollbackPanel from './components/RollbackPanel.vue'
import ArchivePanel from './components/ArchivePanel.vue'

const { t, locale } = useI18n()

const workflowSteps = [
  { id: 'scan', key: 'tabs.scan', descKey: 'stage.scan', number: '01' },
  { id: 'rename', key: 'tabs.rename', descKey: 'stage.rename', number: '02' },
  { id: 'archive', key: 'tabs.archive', descKey: 'stage.archive', number: '03' },
  { id: 'rollback', key: 'tabs.rollback', descKey: 'stage.rollback', number: '04' },
  { id: 'workspace', key: 'tabs.workspaces', descKey: 'stage.workspace', number: '05' },
] as const

const activeTab = ref<string>('scan')
const workspaces = ref<WorkspaceEntry[]>([])
const selectedId = ref<string>('')
const customPath = ref('')
const customPathInput = ref<HTMLInputElement | null>(null)
const customPathMode = ref(false)
const showLocalPathDialog = ref(false)
const pendingLocalPath = ref('')
const workspaceLoaded = ref(false)

const languages = [
  { value: 'zh', label: '中文' },
  { value: 'en', label: 'English' },
] as const

type LocaleCode = (typeof languages)[number]['value']

const rootPath = computed(() => {
  if (selectedId.value && !customPathMode.value) {
    const ws = workspaces.value.find((w) => w.id === selectedId.value)
    return ws?.path ?? ''
  }
  return customPath.value
})

const activeStep = computed(() => workflowSteps.find((step) => step.id === activeTab.value))

async function loadWorkspaces() {
  try {
    if (isTauri()) {
      const ws = await native.getRecentWorkspaces()
      workspaces.value = ws
      if (ws.length > 0) {
        selectedId.value = ws[0].id
      }
    } else {
      const data = await api.listWorkspaces()
      workspaces.value = data.workspaces
      if (data.default_workspace_id && workspaces.value.some((w) => w.id === data.default_workspace_id)) {
        selectedId.value = data.default_workspace_id
      } else if (workspaces.value.length > 0) {
        selectedId.value = workspaces.value[0].id
      }
    }
  } catch {
    // workspaces unavailable — user can still type a path
  } finally {
    workspaceLoaded.value = true
  }
}

function changeLocale(event: Event) {
  const target = event.target as HTMLSelectElement
  if (languages.some((item) => item.value === target.value)) {
    setLocale(target.value as LocaleCode)
  }
}

async function chooseLocalDirectory() {
  if (isTauri()) {
    const path = await native.chooseDirectory()
    if (path) {
      customPath.value = path
      customPathMode.value = true
      selectedId.value = ''
      await native.saveRecentWorkspace(path)
      await loadWorkspaces()
    }
    return
  }
  pendingLocalPath.value = customPath.value
  showLocalPathDialog.value = true
  await nextTick()
  customPathInput.value?.focus()
}

function handleWorkspaceSelection() {
  customPathMode.value = !selectedId.value
}

async function applyLocalDirectory() {
  if (!pendingLocalPath.value.trim()) {
    await nextTick()
    customPathInput.value?.focus()
    return
  }
  customPath.value = pendingLocalPath.value.trim()
  customPathMode.value = true
  selectedId.value = ''
  showLocalPathDialog.value = false
}

onMounted(loadWorkspaces)
</script>

<template>
  <div class="app">
    <header class="app-header">
      <div>
        <h1>{{ t('app.title') }}</h1>
        <p>{{ t('app.subtitle') }}</p>
      </div>
      <div class="header-actions">
        <span class="status-pill">{{ rootPath ? t('app.workspaceReady') : t('app.workspaceMissing') }}</span>
        <label class="language-select">
          <span>{{ t('app.language') }}</span>
          <select :value="locale" @change="changeLocale">
            <option v-for="item in languages" :key="item.value" :value="item.value">
              {{ item.label }}
            </option>
          </select>
        </label>
      </div>
    </header>

    <section class="workspace-shell">
      <div class="workspace-copy">
        <span class="eyebrow">{{ t('app.directory') }}</span>
        <strong>{{ rootPath || t('app.noDirectory') }}</strong>
        <span v-if="!workspaceLoaded" class="ws-hint">{{ t('app.loading') }}</span>
        <span v-else-if="workspaces.length === 0 && !customPath" class="ws-hint">
          {{ t('app.noWorkspaceHint') }}
        </span>
      </div>
      <div class="workspace-controls">
        <select v-model="selectedId" class="ws-select" @change="handleWorkspaceSelection">
          <option value="" disabled>{{ t('app.selectWorkspace') }}</option>
          <option v-for="ws in workspaces" :key="ws.id" :value="ws.id">
            {{ ws.name }} — {{ ws.path }}
          </option>
          <option value="">{{ t('app.customPath') }}</option>
        </select>
        <button class="btn btn-secondary" type="button" @click="chooseLocalDirectory">
          {{ isTauri() ? t('app.chooseFolder') : t('app.chooseLocalDirectory') }}
        </button>
        <button
          v-if="isTauri() && rootPath"
          class="btn btn-secondary"
          type="button"
          @click="native.revealInFinder(rootPath)"
        >
          {{ t('app.revealInFinder') }}
        </button>
        <span v-if="customPathMode && customPath" class="custom-path-pill">
          {{ t('app.customPathActive') }}
        </span>
        <span v-if="customPathMode" class="ws-path-help">
          {{ t('app.localDirectoryHint') }}
        </span>
      </div>
    </section>

    <div
      v-if="showLocalPathDialog"
      class="local-path-backdrop"
      @click.self="showLocalPathDialog = false"
    >
      <section class="local-path-dialog">
        <div class="dialog-header">
          <span class="eyebrow">{{ t('app.directory') }}</span>
          <h2>{{ t('app.localDirectoryTitle') }}</h2>
          <p>{{ t('app.localDirectoryDescription') }}</p>
        </div>
        <label class="local-path-field">
          <span>{{ t('app.localDirectoryPathLabel') }}</span>
          <input
            ref="customPathInput"
            v-model="pendingLocalPath"
            type="text"
            :placeholder="t('app.customPathPlaceholder')"
            @keyup.enter="applyLocalDirectory"
          />
        </label>
        <div class="path-example">
          <span>{{ t('app.localDirectoryExampleLabel') }}</span>
          <code>/Users/henryzhuhr/Photograph-Raw/Travel/Shanghai</code>
        </div>
        <p class="dialog-note">{{ t('app.localDirectoryHint') }}</p>
        <div class="dialog-actions">
          <button class="btn btn-secondary" type="button" @click="showLocalPathDialog = false">
            {{ t('common.cancel') }}
          </button>
          <button class="btn btn-primary" type="button" @click="applyLocalDirectory">
            {{ t('app.applyLocalDirectory') }}
          </button>
        </div>
      </section>
    </div>

    <div class="workflow-layout">
      <aside class="workflow-nav" :aria-label="t('app.workflow')">
        <button
          v-for="step in workflowSteps"
          :key="step.id"
          :class="['workflow-step', { active: activeTab === step.id }]"
          @click="activeTab = step.id"
        >
          <span class="step-marker">{{ step.number }}</span>
          <span>
            <span class="step-label">{{ t(step.key) }}</span>
            <span class="step-desc">{{ t(step.descKey) }}</span>
          </span>
        </button>
      </aside>

      <main class="main-content">
        <div class="panel-heading">
          <div>
            <span class="eyebrow">{{ t('app.currentStep') }}</span>
            <h2>{{ activeStep ? t(activeStep.key) : '' }}</h2>
            <p>{{ activeStep ? t(activeStep.descKey) : '' }}</p>
          </div>
        </div>

        <ScanPanel v-if="activeTab === 'scan'" :root-path="rootPath" />
        <RenamePanel v-if="activeTab === 'rename'" :root-path="rootPath" />
        <RollbackPanel v-if="activeTab === 'rollback'" :root-path="rootPath" />
        <ArchivePanel v-if="activeTab === 'archive'" :root-path="rootPath" />
        <WorkspacePanel
          v-if="activeTab === 'workspace'"
          :workspaces="workspaces"
          @updated="loadWorkspaces()"
        />
      </main>
    </div>
  </div>
</template>

<style>
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --bg: #f6f7f9;
  --surface: #ffffff;
  --surface-subtle: #f9fafb;
  --border: #d9dee7;
  --text: #1f2937;
  --text-secondary: #667085;
  --primary: #176b87;
  --primary-hover: #12576e;
  --danger: #b42318;
  --danger-hover: #912018;
  --warning-bg: #fff7e6;
  --warning-text: #8a4b0f;
  --error-bg: #fff1f0;
  --error-text: #b42318;
  --success-bg: #ecfdf3;
  --success-text: #067647;
  --radius: 8px;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background:
    linear-gradient(180deg, #eef4f6 0, rgba(238, 244, 246, 0) 280px),
    var(--bg);
  color: var(--text);
  line-height: 1.5;
}

.app {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 16px 48px;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 28px 0 18px;
}

.app-header h1 {
  font-size: 1.625rem;
  font-weight: 700;
  color: var(--text);
}

.app-header p {
  margin-top: 2px;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-pill {
  border: 1px solid var(--border);
  border-radius: 999px;
  background: #edf7f8;
  color: var(--primary);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 10px;
  white-space: nowrap;
}

.language-select {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.language-select select {
  padding: 4px 28px 4px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--text);
  font-size: 0.8125rem;
}

.language-select select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.16);
}

.workspace-shell {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: 0 10px 30px rgba(31, 41, 55, 0.06);
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.workspace-copy {
  display: flex;
  min-width: 260px;
  flex: 1;
  flex-direction: column;
  gap: 2px;
}

.workspace-copy strong {
  overflow-wrap: anywhere;
}

.workspace-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.eyebrow {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0;
  white-space: nowrap;
}

.ws-select {
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 0.875rem;
  background: var(--surface);
  min-width: 260px;
  max-width: 400px;
}

.ws-select:focus {
  outline: none;
  border-color: var(--primary);
}

.ws-custom-input {
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 0.8125rem;
  font-family: 'SF Mono', Menlo, Monaco, monospace;
  min-width: 300px;
  flex: 1;
}

.ws-custom-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}

.ws-hint {
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.ws-path-help {
  flex-basis: 100%;
  color: var(--text-secondary);
  font-size: 0.75rem;
  text-align: right;
}

.custom-path-pill {
  border: 1px solid #b9dce4;
  border-radius: 999px;
  background: #eef8fa;
  color: var(--primary);
  font-size: 0.75rem;
  font-weight: 700;
  padding: 5px 10px;
}

.local-path-backdrop {
  position: fixed;
  inset: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(17, 24, 39, 0.46);
  padding: 20px;
}

.local-path-dialog {
  width: min(640px, 100%);
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--surface);
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.28);
  padding: 22px;
}

.dialog-header {
  border-bottom: 1px solid var(--border);
  padding-bottom: 14px;
  margin-bottom: 16px;
}

.dialog-header h2 {
  margin-top: 4px;
  font-size: 1.25rem;
}

.dialog-header p,
.dialog-note {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.local-path-field {
  display: grid;
  gap: 6px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.local-path-field input {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text);
  font-family: 'SF Mono', Menlo, Monaco, monospace;
  font-size: 0.875rem;
  padding: 10px 12px;
}

.local-path-field input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(23, 107, 135, 0.16);
}

.path-example {
  display: flex;
  flex-direction: column;
  gap: 4px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface-subtle);
  margin: 12px 0;
  padding: 10px 12px;
}

.path-example span {
  color: var(--text-secondary);
  font-size: 0.75rem;
  font-weight: 700;
}

.path-example code {
  color: var(--primary);
  font-size: 0.8125rem;
  overflow-wrap: anywhere;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 18px;
}

.workflow-layout {
  display: grid;
  grid-template-columns: 252px minmax(0, 1fr);
  gap: 20px;
}

.workflow-nav {
  position: relative;
  align-self: start;
  display: flex;
  flex-direction: column;
  gap: 2px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: 0 10px 30px rgba(31, 41, 55, 0.05);
  padding: 14px 12px;
}

.workflow-nav::before {
  position: absolute;
  top: 31px;
  bottom: 31px;
  left: 31px;
  width: 2px;
  background: #e5e7eb;
  content: '';
}

.workflow-step {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr);
  align-items: center;
  gap: 12px;
  width: 100%;
  border: 1px solid transparent;
  border-radius: 7px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 10px;
  text-align: left;
}

.workflow-step:hover {
  background: #f8fafc;
  color: var(--text);
}

.workflow-step.active {
  background: #eef8fa;
  border-color: #b9dce4;
  color: var(--primary);
}

.step-marker {
  display: grid;
  width: 18px;
  height: 18px;
  place-items: center;
  border: 2px solid #cbd5e1;
  border-radius: 999px;
  background: var(--surface);
  color: var(--text-secondary);
  font-size: 0.75rem;
  font-weight: 700;
  line-height: 1;
}

.workflow-step.active .step-marker {
  border-color: var(--primary);
  background: var(--primary);
  color: #fff;
}

.step-label {
  display: block;
  font-size: 0.9375rem;
  font-weight: 600;
}

.step-desc {
  display: block;
  margin-top: 2px;
  color: var(--text-secondary);
  font-size: 0.75rem;
  line-height: 1.3;
}

.main-content {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: 0 10px 30px rgba(31, 41, 55, 0.06);
  padding: 26px;
  min-width: 0;
}

.panel-heading {
  border-bottom: 1px solid var(--border);
  margin-bottom: 20px;
  padding-bottom: 16px;
}

.panel-heading h2 {
  margin-top: 2px;
  font-size: 1.25rem;
  font-weight: 700;
}

.panel-heading p {
  margin-top: 4px;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* ---- Shared form styles ---- */
.panel h2 {
  display: none;
}

.form-row {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-group input {
  padding: 9px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 0.875rem;
  font-family: monospace;
  min-width: 280px;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}

.btn {
  padding: 9px 16px;
  border: none;
  border-radius: var(--radius);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s;
  white-space: nowrap;
}

.btn-primary {
  background: var(--primary);
  color: #fff;
}

.btn-primary:hover {
  background: var(--primary-hover);
}

.btn-danger {
  background: var(--danger);
  color: #fff;
}

.btn-danger:hover {
  background: var(--danger-hover);
}

.btn-secondary {
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
}

.btn-secondary:hover {
  background: var(--surface-subtle);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.result-section {
  margin-top: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
  table-layout: fixed;
}

thead {
  background: var(--surface-subtle);
}

th {
  text-align: left;
  padding: 8px 12px;
  font-weight: 600;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}

td {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
  overflow-wrap: anywhere;
}

tr:hover td {
  background: #fafafa;
}

.mono {
  font-family: 'SF Mono', 'Menlo', 'Monaco', monospace;
  font-size: 0.8125rem;
}

.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge-raw {
  background: #dbeafe;
  color: #1e40af;
}

.badge-sidecar {
  background: #e0e7ff;
  color: #3730a3;
}

.badge-other {
  background: #f3f4f6;
  color: #6b7280;
}

.badge-pending {
  background: #fef3c7;
  color: #92400e;
}

.badge-renamed {
  background: #d1fae5;
  color: #065f46;
}

.badge-rolled_back {
  background: #f3f4f6;
  color: #6b7280;
}

.alert {
  padding: 12px 16px;
  border-radius: var(--radius);
  margin-bottom: 12px;
  font-size: 0.8125rem;
}

.alert-warning {
  background: var(--warning-bg);
  color: var(--warning-text);
}

.alert-error {
  background: var(--error-bg);
  color: var(--error-text);
}

.summary {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  min-width: 128px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 10px 12px;
  background: var(--surface-subtle);
}

.summary-value {
  font-size: 1.5rem;
  font-weight: 700;
}

.summary-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.empty-state {
  color: var(--text-secondary);
  font-size: 0.875rem;
  padding: 16px 0;
}

.actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

@media (max-width: 840px) {
  .app-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .workflow-layout {
    grid-template-columns: 1fr;
  }

  .workflow-nav {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .workflow-nav::before {
    display: none;
  }

  .workspace-controls,
  .ws-select,
  .ws-custom-input {
    width: 100%;
    min-width: 0;
    max-width: none;
  }
}
</style>
