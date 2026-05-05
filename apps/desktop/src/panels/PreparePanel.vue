<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useJourney } from '../composables/useJourney'
import { native } from '@/platform'
import { onMounted, ref } from 'vue'

const { t } = useI18n()
const { projectRoot, setProjectRoot, goToStep } = useJourney()
const recentDirs = ref<Array<{ id: string; name: string; path: string }>>([])

onMounted(async () => {
  recentDirs.value = await native.getRecentWorkspaces()
})

async function chooseDirectory() {
  const path = await native.chooseDirectory()
  if (path) {
    setProjectRoot(path)
    await native.saveRecentWorkspace(path)
    recentDirs.value = await native.getRecentWorkspaces()
    goToStep('scan')
  }
}

async function removeRecent(id: string) {
  await native.forgetWorkspace(id)
  recentDirs.value = await native.getRecentWorkspaces()
}

function selectRecent(dir: { path: string }) {
  setProjectRoot(dir.path)
  goToStep('scan')
}
</script>

<template>
  <section>
    <div class="stage-note">
      <strong>{{ t('prepare.guideTitle') }}</strong>
      <span>{{ t('prepare.guideBody') }}</span>
    </div>

    <button class="btn primary" @click="chooseDirectory" style="margin-bottom:18px">
      {{ t('prepare.selectDirAction') }}
    </button>

    <div v-if="projectRoot" class="alert alert-success">
      {{ t('prepare.dirAccessible') }}: <span class="mono">{{ projectRoot }}</span>
    </div>

    <div class="panel-card panel-pad" style="margin-top:16px">
      <span class="eyebrow">{{ t('prepare.recentDirs') }}</span>
      <div v-if="recentDirs.length === 0" class="empty-state" style="margin-top:8px">
        {{ t('prepare.noRecentDirs') }}
      </div>
      <div v-else class="recent-list">
        <button
          v-for="dir in recentDirs"
          :key="dir.id"
          class="recent-row"
          @click="selectRecent(dir)"
        >
          <span>
            <strong>{{ dir.name }}</strong>
            <small class="mono">{{ dir.path }}</small>
          </span>
          <button class="btn" @click.stop="removeRecent(dir.id)">
            {{ t('projectBar.removeRecent') }}
          </button>
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.stage-note {
  display: flex;
  flex-direction: column;
  gap: 4px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--panel-soft);
  padding: 12px 14px;
  margin-bottom: 16px;
}

.stage-note strong { font-size: 14px; }
.stage-note span { color: var(--muted); font-size: 13px; }

.recent-list {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}

.recent-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--panel);
  color: var(--ink);
  cursor: pointer;
  padding: 12px;
  text-align: left;
  font: inherit;
}

.recent-row:hover {
  border-color: var(--accent-line);
  background: var(--accent-soft);
}

.recent-row strong { display: block; font-size: 14px; }
.recent-row small { display: block; margin-top: 2px; color: var(--muted); }
</style>
