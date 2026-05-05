<script setup lang="ts">
import { useJourney } from './composables/useJourney'
import TopBar from './components/TopBar.vue'
import ProjectBar from './components/ProjectBar.vue'
import JourneySidebar from './components/JourneySidebar.vue'
import InspectorPanel from './components/InspectorPanel.vue'
import PreparePanel from './panels/PreparePanel.vue'
import ScanPanel from './panels/ScanPanel.vue'
import NamingPanel from './panels/NamingPanel.vue'
import ExecutePanel from './panels/ExecutePanel.vue'
import PostProcessPanel from './panels/PostProcessPanel.vue'
import ArchivePanel from './panels/ArchivePanel.vue'
import SettingsPage from './pages/SettingsPage.vue'
import SafetyPage from './pages/SafetyPage.vue'
import './theme.css'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'

const { t } = useI18n()
const { activeStep, isUtilityPage, utilityPage } = useJourney()

const stepLabel = computed(() => {
  const map: Record<string, string> = {
    prepare: 'journey.prepare',
    scan: 'journey.scan',
    naming: 'journey.naming',
    execute: 'journey.execute',
    postprocess: 'journey.postprocess',
    archive: 'journey.archive',
  }
  return map[activeStep.value] || ''
})
</script>

<template>
  <div class="desktop-shell">
    <TopBar />
    <ProjectBar />
    <div class="workbench">
      <JourneySidebar />

      <!-- Utility Pages -->
      <main class="main" v-if="isUtilityPage">
        <SettingsPage v-if="utilityPage === 'settings'" />
        <SafetyPage v-if="utilityPage === 'safety'" />
      </main>

      <!-- Workflow Stage -->
      <main class="main" v-else>
        <div class="stage-heading">
          <div>
            <span class="eyebrow">{{ t('app.currentStep') }}</span>
            <h3>{{ t(stepLabel) }}</h3>
          </div>
        </div>

        <PreparePanel v-if="activeStep === 'prepare'" />
        <ScanPanel v-if="activeStep === 'scan'" />
        <NamingPanel v-if="activeStep === 'naming'" />
        <ExecutePanel v-if="activeStep === 'execute'" />
        <PostProcessPanel v-if="activeStep === 'postprocess'" />
        <ArchivePanel v-if="activeStep === 'archive'" />
      </main>

      <InspectorPanel />
    </div>
  </div>
</template>

<style>
.desktop-shell {
  max-width: 1560px;
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.workbench {
  display: grid;
  grid-template-columns: 238px minmax(0, 1fr) 278px;
  min-height: 720px;
  flex: 1;
}

.main {
  padding: 22px;
}

.stage-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 16px;
}

.stage-heading h3 {
  margin: 0;
  font-size: 22px;
}
</style>
