<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useJourney } from '../composables/useJourney'

const { t } = useI18n()
const { postprocessDone, goToStep } = useJourney()

function markDone() {
  postprocessDone.value = true
  goToStep('archive')
}
</script>

<template>
  <section>
    <div class="stage-note">
      <strong>{{ t('postprocess.guideTitle') }}</strong>
      <span>{{ t('postprocess.guideBody') }}</span>
    </div>

    <div class="panel-card panel-pad" style="margin-bottom:14px">
      <div style="display:flex;align-items:center;gap:12px">
        <span style="font-size:32px">{{ postprocessDone ? '✅' : '⏳' }}</span>
        <div>
          <strong style="font-size:15px" v-if="postprocessDone">{{ t('postprocess.done') }}</strong>
          <strong style="font-size:15px" v-else>{{ t('postprocess.notDone') }}</strong>
          <p style="margin-top:4px;color:var(--muted);font-size:13px">{{ t('postprocess.reminder') }}</p>
        </div>
      </div>
    </div>

    <button v-if="!postprocessDone" class="btn primary" @click="markDone">
      {{ t('postprocess.markDone') }}
    </button>
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
</style>
