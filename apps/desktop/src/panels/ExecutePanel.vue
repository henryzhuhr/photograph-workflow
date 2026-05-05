<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { api, type RenamePlan, type RenamePlanItem } from '@/api'
import { useJourney } from '../composables/useJourney'
import DirectoryTree, { type DirNode } from '../components/DirectoryTree.vue'

const { t } = useI18n()
const { projectRoot, renamePlan, goToStep } = useJourney()
const executing = ref(false)
const showConfirm = ref(false)
const error = ref('')
const completed = ref(false)

const plan = computed(() => renamePlan.value as RenamePlan | null)

const rawCount = computed(() => plan.value?.items?.filter((i: any) => i.role === 'raw').length ?? 0)
const sidecarCount = computed(() => plan.value?.items?.filter((i: any) => i.role === 'sidecar').length ?? 0)

const canExecute = computed(() => {
  if (!plan.value) return false
  return (plan.value.errors?.length ?? 0) === 0 && (plan.value.items?.length ?? 0) > 0
})

// Build directory tree from plan items
const dirTree = computed<DirNode[]>(() => {
  if (!plan.value?.items) return []
  const items = plan.value.items

  // Group by directory
  const dirMap = new Map<string, RenamePlanItem[]>()
  for (const item of items) {
    const dir = item.target_path ? item.target_path.split('/').slice(0, -1).join('/') || '.' : '.'
    if (!dirMap.has(dir)) dirMap.set(dir, [])
    dirMap.get(dir)!.push(item)
  }

  const nodes: DirNode[] = []
  for (const [dirPath, dirItems] of dirMap) {
    const name = dirPath === '.' ? '.' : dirPath.split('/').pop() || dirPath
    const rawItems = dirItems.filter((i) => i.role === 'raw')
    const scItems = dirItems.filter((i) => i.role === 'sidecar')
    const hasErrs = plan.value?.errors?.some((e: any) => e.path?.startsWith(dirPath))

    nodes.push({
      name,
      path: dirPath,
      rawCount: rawItems.length,
      sidecarCount: scItems.length,
      status: hasErrs ? 'error' : 'ready',
      statusLabel: hasErrs ? t('naming.warning') : t('execute.noConflicts'),
      hasSubdir: false,
      subdirCount: 0,
      items: dirItems.map((i) => ({
        sourceName: (i as any).current_name || (i as any).source_path?.split('/').pop() || '',
        targetName: (i as any).planned_name || (i as any).target_path?.split('/').pop() || '',
        role: i.role as 'raw' | 'sidecar',
      })),
    })
  }
  return nodes
})

async function execute() {
  if (!projectRoot.value) return
  executing.value = true
  error.value = ''
  try {
    renamePlan.value = await api.renameExecute(projectRoot.value)
    completed.value = true
    showConfirm.value = false
  } catch {
    error.value = t('common.errorExecute')
  } finally {
    executing.value = false
  }
}

function confirmAndExecute() {
  showConfirm.value = true
}

function finish() {
  goToStep('postprocess')
}
</script>

<template>
  <section>
    <div class="stage-note">
      <strong>{{ t('execute.guideTitle') }}</strong>
      <span>{{ t('execute.guideBody') }}</span>
    </div>

    <div v-if="!plan && !completed" class="empty-state">
      {{ t('execute.empty') }}
    </div>

    <div v-if="plan" class="panel-card panel-pad" style="margin-bottom:14px">
      <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px">
        <div>
          <span class="eyebrow">{{ t('execute.renamePreview') }}</span>
          <h3 style="margin:2px 0;font-size:18px">{{ t('execute.previewByDirectory') }}</h3>
        </div>
        <span class="pill info">{{ plan.items?.length ?? 0 }} {{ t('execute.filesCount') }}</span>
      </div>
      <DirectoryTree :directories="dirTree" :open="true" />
    </div>

    <div v-if="completed" class="alert alert-success">
      <strong>{{ t('execute.completeTitle') }}</strong>
      <p style="margin-top:4px">{{ t('execute.completeBody') }}</p>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div class="actions" v-if="!completed">
      <button
        v-if="plan && canExecute"
        class="btn primary"
        @click="confirmAndExecute"
      >
        {{ executing ? t('execute.executing') : t('execute.executeRename') }}
      </button>
      <button v-if="completed" class="btn primary" @click="finish">
        {{ t('postprocess.markDone') }}
      </button>
    </div>

    <!-- Confirm modal -->
    <div v-if="showConfirm" class="confirm-backdrop" @click.self="showConfirm = false">
      <div class="confirm-modal">
        <h3>{{ t('execute.confirmTitle') }}</h3>
        <p>{{ t('execute.confirmBody') }}</p>
        <div class="summary-grid" style="margin-top:14px">
          <div class="summary-item">
            <div class="summary-value">{{ rawCount }}</div>
            <div class="summary-label">{{ t('scan.rawDng') }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-value">{{ sidecarCount }}</div>
            <div class="summary-label">{{ t('scan.sidecars') }}</div>
          </div>
        </div>
        <div class="actions">
          <button class="btn" @click="showConfirm = false">{{ t('common.cancel') }}</button>
          <button class="btn danger" :disabled="executing" @click="execute">
            {{ t('execute.confirmExecute') }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.stage-note {
  display: flex; flex-direction: column; gap: 4px;
  border: 1px solid var(--line); border-radius: var(--radius);
  background: var(--panel-soft); padding: 12px 14px; margin-bottom: 16px;
}
.stage-note strong { font-size: 14px; }
.stage-note span { color: var(--muted); font-size: 13px; }

.actions { display: flex; gap: 8px; margin-top: 16px; }

.confirm-backdrop {
  position: fixed; inset: 0; z-index: 30;
  display: flex; align-items: center; justify-content: center;
  background: rgba(17, 24, 39, 0.46); padding: 20px;
}
.confirm-modal {
  width: min(480px, 100%);
  border: 1px solid var(--line); border-radius: 10px;
  background: var(--panel); box-shadow: 0 24px 80px rgba(15, 23, 42, 0.28);
  padding: 22px;
}
.confirm-modal h3 { font-size: 1.15rem; }
.confirm-modal p { margin-top: 8px; color: var(--muted); font-size: 13px; }
</style>
