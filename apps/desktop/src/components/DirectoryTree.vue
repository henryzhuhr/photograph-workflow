<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

export interface DirNode {
  name: string
  path: string
  rawCount: number
  sidecarCount: number
  status: 'ready' | 'warning' | 'error'
  statusLabel: string
  hasSubdir: boolean
  subdirCount: number
  items: Array<{
    sourceName: string
    targetName: string
    role: 'raw' | 'sidecar'
  }>
  children?: DirNode[]
}

defineProps<{
  directories: DirNode[]
  open?: boolean
}>()
</script>

<template>
  <div class="rename-plan">
    <template v-for="dir in directories" :key="dir.path">
      <details :class="['rename-directory', { nested: false }]" :open="open ?? true">
        <summary>
          <span class="tree-caret">›</span>
          <div>
            <strong>{{ dir.name }}</strong>
            <small>{{ t('execute.rawWithSidecars', { raw: dir.rawCount, sidecar: dir.sidecarCount }) }}</small>
          </div>
          <span :class="['pill', dir.status]">{{ dir.statusLabel }}</span>
        </summary>
        <div class="rename-children">
          <!-- File-level items -->
          <div
            v-for="item in dir.items"
            :key="item.sourceName"
            :class="['rename-line', { sidecar: item.role === 'sidecar' }]"
          >
            <span>{{ item.sourceName }}</span>
            <span class="arrow">→</span>
            <span>{{ item.targetName }}</span>
          </div>
          <!-- Nested subdirectories -->
          <DirectoryTree
            v-if="dir.children && dir.children.length > 0"
            :directories="dir.children"
            :open="false"
          />
        </div>
      </details>
    </template>
  </div>
</template>

<style scoped>
.rename-plan {
  display: grid;
  gap: 8px;
  margin-top: 14px;
}

.rename-directory {
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--panel);
  overflow: hidden;
}

.rename-directory summary {
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  cursor: pointer;
  list-style: none;
  padding: 12px;
}

.rename-directory summary::-webkit-details-marker {
  display: none;
}

.rename-directory summary strong {
  display: block;
  font-size: 14px;
}

.rename-directory summary small {
  display: block;
  margin-top: 2px;
  color: var(--muted);
  font-size: 12px;
}

.tree-caret {
  color: var(--muted);
  font-size: 18px;
  transform: rotate(0deg);
  transition: transform 160ms ease;
}

.rename-directory[open] > summary .tree-caret {
  transform: rotate(90deg);
}

.rename-children {
  display: grid;
  gap: 8px;
  border-top: 1px solid var(--line);
  padding: 10px 12px 12px 44px;
}

.rename-line {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 24px minmax(0, 1.2fr);
  gap: 10px;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--panel-soft);
  padding: 10px;
  font-family: "SF Mono", Menlo, Consolas, monospace;
  font-size: 12px;
}

.rename-line.sidecar {
  background: var(--panel);
  color: var(--muted);
}

.arrow {
  color: var(--muted);
  text-align: center;
}
</style>
