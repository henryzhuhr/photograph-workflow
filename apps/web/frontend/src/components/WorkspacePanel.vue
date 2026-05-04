<script setup lang="ts">
import { api, type WorkspaceEntry, type WorkspaceFile } from '../api'
import { onMounted, ref } from 'vue'

const workspaces = ref<WorkspaceEntry[]>([])
const defaultId = ref<string | null>(null)
const loading = ref(false)
const error = ref('')

const newPath = ref('')
const newName = ref('')
const adding = ref(false)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await api.listWorkspaces()
    workspaces.value = data.workspaces
    defaultId.value = data.default_workspace_id
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to load'
  } finally {
    loading.value = false
  }
}

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
      await load()
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
    await load()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to remove'
  }
}

async function setDefault(id: string) {
  error.value = ''
  try {
    await api.setDefaultWorkspace(id)
    await load()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to set default'
  }
}

onMounted(load)
</script>

<template>
  <div class="panel">
    <h2>Workspaces</h2>

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

    <div v-if="loading" class="empty-state">Loading...</div>

    <div v-else-if="workspaces.length === 0" class="empty-state">
      No workspaces saved yet. Add one above.
    </div>

    <table v-else>
      <thead>
        <tr>
          <th>Name</th>
          <th>Path</th>
          <th>Kind</th>
          <th>Default</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="ws in workspaces" :key="ws.id">
          <td>{{ ws.name }}</td>
          <td class="mono">{{ ws.path }}</td>
          <td><span class="badge badge-other">{{ ws.kind }}</span></td>
          <td>
            <span v-if="ws.id === defaultId" class="badge badge-renamed">Default</span>
            <button v-else class="btn btn-secondary" @click="setDefault(ws.id)">Set Default</button>
          </td>
          <td>
            <button class="btn btn-danger" @click="remove(ws.id)">Remove</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
