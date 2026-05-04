<script setup lang="ts">
import { api, type WorkspaceEntry } from '../api'
import { ref } from 'vue'

const props = defineProps<{
  workspaces: WorkspaceEntry[]
}>()

const emit = defineEmits<{
  updated: []
}>()

const newPath = ref('')
const newName = ref('')
const adding = ref(false)
const error = ref('')

async function add() {
  if (!newPath.value.trim()) return
  adding.value = true
  error.value = ''
  try {
    const plan = await api.addWorkspace(newPath.value.trim(), newName.value.trim() || undefined)
    if (plan.errors.length > 0) {
      error.value = plan.errors.map((e) => e.message).join('; ')
    } else {
      newPath.value = ''
      newName.value = ''
      emit('updated')
    }
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to add'
  } finally {
    adding.value = false
  }
}

async function remove(id: string) {
  error.value = ''
  try {
    const plan = await api.removeWorkspace(id)
    if (plan.errors.length > 0) {
      error.value = plan.errors.map((e) => e.message).join('; ')
    }
    emit('updated')
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to remove'
  }
}

async function setDefault(id: string) {
  error.value = ''
  try {
    await api.setDefaultWorkspace(id)
    emit('updated')
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to set default'
  }
}

function defaultId() {
  // Find default from the workspace file — since we don't have the file-level defaultId,
  // we read it from the parent. For now, let's approximate by getting the first one.
  // The actual default is tracked in App.vue's selectedId which is a different concept.
  return null
}
</script>

<template>
  <div class="panel">
    <h2>Workspaces</h2>
    <p style="color: var(--text-secondary); font-size: 0.8125rem; margin-bottom: 16px">
      Saved directories appear in the selector at the top of the page.
    </p>

    <div class="form-row">
      <div class="form-group">
        <label>Directory Path</label>
        <input v-model="newPath" type="text" placeholder="/path/to/photos" @keyup.enter="add()" />
      </div>
      <div class="form-group">
        <label>Name (optional)</label>
        <input v-model="newName" type="text" placeholder="My Photos" @keyup.enter="add()" />
      </div>
      <button class="btn btn-primary" :disabled="adding || !newPath.trim()" @click="add()">
        {{ adding ? 'Adding...' : 'Add Workspace' }}
      </button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div v-if="props.workspaces.length === 0" class="empty-state">
      No workspaces saved yet. Add one above.
    </div>

    <table v-else>
      <thead>
        <tr>
          <th>Name</th>
          <th>Path</th>
          <th>Kind</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="ws in props.workspaces" :key="ws.id">
          <td>{{ ws.name }}</td>
          <td class="mono">{{ ws.path }}</td>
          <td><span class="badge badge-other">{{ ws.kind }}</span></td>
          <td>
            <button class="btn btn-danger" @click="remove(ws.id)">Remove</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
