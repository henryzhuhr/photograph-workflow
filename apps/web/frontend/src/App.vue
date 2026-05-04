<script setup lang="ts">
import { ref } from 'vue'
import WorkspacePanel from './components/WorkspacePanel.vue'
import ScanPanel from './components/ScanPanel.vue'
import RenamePanel from './components/RenamePanel.vue'
import RollbackPanel from './components/RollbackPanel.vue'
import ArchivePanel from './components/ArchivePanel.vue'

const tabs = [
  { id: 'workspace', label: 'Workspace' },
  { id: 'scan', label: 'Scan' },
  { id: 'rename', label: 'Rename' },
  { id: 'rollback', label: 'Rollback' },
  { id: 'archive', label: 'Archive' },
] as const

const activeTab = ref<string>('workspace')
</script>

<template>
  <div class="app">
    <header class="app-header">
      <h1>Photograph Workflow</h1>
    </header>
    <nav class="tab-bar">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </nav>
    <main class="main-content">
      <WorkspacePanel v-if="activeTab === 'workspace'" />
      <ScanPanel v-if="activeTab === 'scan'" />
      <RenamePanel v-if="activeTab === 'rename'" />
      <RollbackPanel v-if="activeTab === 'rollback'" />
      <ArchivePanel v-if="activeTab === 'archive'" />
    </main>
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
  --bg: #f5f5f5;
  --surface: #ffffff;
  --border: #e0e0e0;
  --text: #333333;
  --text-secondary: #666666;
  --primary: #2563eb;
  --primary-hover: #1d4ed8;
  --danger: #dc2626;
  --danger-hover: #b91c1c;
  --warning-bg: #fef3c7;
  --warning-text: #92400e;
  --error-bg: #fee2e2;
  --error-text: #991b1b;
  --success-bg: #d1fae5;
  --success-text: #065f46;
  --radius: 6px;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
}

.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px 48px;
}

.app-header {
  padding: 24px 0 16px;
}

.app-header h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text);
}

.tab-bar {
  display: flex;
  gap: 4px;
  border-bottom: 2px solid var(--border);
  margin-bottom: 24px;
}

.tab {
  padding: 8px 20px;
  border: none;
  background: none;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: color 0.15s, border-color 0.15s;
}

.tab:hover {
  color: var(--text);
}

.tab.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}

.main-content {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
}

/* Shared form styles */
.panel h2 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 16px;
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
  padding: 8px 12px;
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
  padding: 8px 16px;
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
  background: var(--border);
  color: var(--text);
}

.btn-secondary:hover {
  background: #ccc;
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
}

thead {
  background: var(--bg);
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
  gap: 24px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.summary-item {
  display: flex;
  flex-direction: column;
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
</style>
