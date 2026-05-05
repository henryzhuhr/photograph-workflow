<script setup lang="ts">
import { api, type WorkspaceEntry } from '../api'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { isTauri, native } from '../platform'

const { t } = useI18n()

defineProps<{ workspaces: WorkspaceEntry[] }>()

const emit = defineEmits<{ updated: [] }>()

const newPath = ref('')
const newName = ref('')
const adding = ref(false)
const error = ref('')

async function pickDirectory() {
  const path = await native.chooseDirectory()
  if (path) newPath.value = path
}

async function add() {
  if (!newPath.value.trim()) return
  adding.value = true
  error.value = ''
  try {
    if (isTauri()) {
      await native.saveRecentWorkspace(newPath.value.trim(), newName.value.trim() || undefined)
      newPath.value = ''
      newName.value = ''
      emit('updated')
    } else {
      const plan = await api.addWorkspace(newPath.value.trim(), newName.value.trim() || undefined)
      if (plan.errors.length > 0) {
        error.value = plan.errors.map((e) => e.message).join('; ')
      } else {
        newPath.value = ''
        newName.value = ''
        emit('updated')
      }
    }
  } catch {
    error.value = t('common.errorAdd')
  } finally {
    adding.value = false
  }
}

async function remove(id: string) {
  error.value = ''
  try {
    if (isTauri()) {
      await native.forgetWorkspace(id)
    } else {
      const plan = await api.removeWorkspace(id)
      if (plan.errors.length > 0) {
        error.value = plan.errors.map((e) => e.message).join('; ')
      }
    }
    emit('updated')
  } catch {
    error.value = t('common.errorRemove')
  }
}
</script>

<template>
  <div class="panel">
    <h2>{{ t('workspace.title') }}</h2>
    <section class="stage-note">
      <strong>{{ t('workspace.guideTitle') }}</strong>
      <span>{{ t('workspace.hint') }}</span>
    </section>

    <div class="form-row">
      <div class="form-group">
        <label>{{ t('workspace.pathLabel') }}</label>
        <div class="path-input-row">
          <input
            v-model="newPath"
            type="text"
            :placeholder="t('workspace.pathPlaceholder')"
            @keyup.enter="add()"
          />
          <button
            v-if="isTauri()"
            class="btn btn-secondary"
            type="button"
            @click="pickDirectory()"
          >
            {{ t('app.chooseFolder') }}
          </button>
        </div>
      </div>
      <div class="form-group">
        <label>{{ t('workspace.nameLabel') }}</label>
        <input
          v-model="newName"
          type="text"
          :placeholder="t('workspace.namePlaceholder')"
          @keyup.enter="add()"
        />
      </div>
      <button class="btn btn-primary" :disabled="adding || !newPath.trim()" @click="add()">
        {{ adding ? t('workspace.adding') : t('workspace.add') }}
      </button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div v-if="$props.workspaces.length === 0" class="empty-state">
      {{ t('workspace.empty') }}
    </div>

    <table v-else>
      <thead>
        <tr>
          <th>{{ t('workspace.nameHeader') }}</th>
          <th>{{ t('workspace.pathHeader') }}</th>
          <th>{{ t('workspace.kindHeader') }}</th>
          <th>{{ t('workspace.actionsHeader') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="ws in $props.workspaces" :key="ws.id">
          <td>{{ ws.name }}</td>
          <td class="mono">{{ ws.path }}</td>
          <td><span class="badge badge-other">{{ ws.kind }}</span></td>
          <td>
            <button class="btn btn-danger" @click="remove(ws.id)">
              {{ t('workspace.remove') }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.stage-note {
  display: flex;
  flex-direction: column;
  gap: 4px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface-subtle);
  padding: 12px 14px;
  margin-bottom: 16px;
}

.stage-note span {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.path-input-row {
  display: flex;
  gap: 8px;
}

.path-input-row input {
  flex: 1;
}
</style>
