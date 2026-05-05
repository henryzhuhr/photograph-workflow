<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useJourney } from '../composables/useJourney'
import { native } from '@/platform'
import { ref } from 'vue'

const { t } = useI18n()
const { projectRoot, setProjectRoot, goToStep } = useJourney()
const showRecent = ref(false)

async function chooseDirectory() {
  const path = await native.chooseDirectory()
  if (path) {
    setProjectRoot(path)
    await native.saveRecentWorkspace(path)
    goToStep('scan')
  }
}

function reveal() {
  if (projectRoot.value) {
    native.revealInFinder(projectRoot.value)
  }
}
</script>

<template>
  <div class="project-bar">
    <div>
      <div class="eyebrow">{{ t('projectBar.currentProject') }}</div>
      <div class="path" v-if="projectRoot">{{ projectRoot }}</div>
      <div class="path muted" v-else>—</div>
    </div>
    <div class="project-actions">
      <button class="btn primary" @click="chooseDirectory">
        {{ t('projectBar.chooseDirectory') }}
      </button>
      <button class="btn" @click="showRecent = !showRecent">
        {{ t('projectBar.recentProjects') }}
      </button>
      <button class="btn" v-if="projectRoot" @click="reveal">
        {{ t('app.revealInFinder') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.project-bar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 20px;
  align-items: center;
  border-bottom: 1px solid var(--line);
  background: var(--panel);
  padding: 18px 20px;
}

.path {
  margin-top: 3px;
  font-family: "SF Mono", Menlo, Consolas, monospace;
  font-size: 13px;
  overflow-wrap: anywhere;
}

.path.muted {
  color: var(--muted);
}

.project-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
</style>
