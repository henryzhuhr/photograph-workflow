<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { api } from '@/api'
import { useJourney } from '../composables/useJourney'
import type { JourneyStep } from '../composables/useJourney'

const { t } = useI18n()
const { projectRoot, renamePlan, goToStep } = useJourney()
const template = ref('{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}')
const templateInput = ref<HTMLInputElement | null>(null)
const loading = ref(false)
const error = ref('')

const tokens = [
  { token: '{date:YYYYMMDD}', labelKey: 'rename.placeholderDate', descKey: 'rename.placeholderDateDesc' },
  { token: '{title}', labelKey: 'rename.placeholderTitle', descKey: 'rename.placeholderTitleDesc' },
  { token: '{date:HHMMSS}', labelKey: 'rename.placeholderTime', descKey: 'rename.placeholderTimeDesc' },
  { token: '{original}', labelKey: 'rename.placeholderOriginal', descKey: 'rename.placeholderOriginalDesc' },
]

function insertPlaceholder(token: string) {
  const input = templateInput.value
  if (input) {
    const start = input.selectionStart ?? template.value.length
    const end = input.selectionEnd ?? start
    template.value = template.value.slice(0, start) + token + template.value.slice(end)
    requestAnimationFrame(() => {
      input.selectionStart = input.selectionEnd = start + token.length
      input.focus()
    })
  } else {
    template.value += token
  }
}

function useDefault() {
  template.value = '{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}'
}

async function generatePlan() {
  if (!projectRoot.value) return
  loading.value = true
  error.value = ''
  try {
    renamePlan.value = await api.renamePlan(projectRoot.value, template.value || undefined)
    goToStep('execute' as JourneyStep)
  } catch {
    error.value = t('common.errorGeneratePlan')
  } finally {
    loading.value = false
  }
}

const liveSample = computed(() => {
  const tpl = template.value || '{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}'
  return tpl
    .replace('{date:YYYYMMDD}', '20260101')
    .replace('{title}', '上海东方明珠')
    .replace('{date:HHMMSS}', '080001')
    .replace('{original}', 'DSC00000')
})
</script>

<template>
  <section>
    <div class="stage-note">
      <strong>{{ t('naming.guideTitle') }}</strong>
      <span>{{ t('naming.guideBody') }}</span>
    </div>

    <div class="panel-card panel-pad template-box">
      <span class="eyebrow">{{ t('naming.templateLabel') }}</span>
      <input
        ref="templateInput"
        v-model="template"
        class="input"
        type="text"
        style="width:100%;margin-top:8px"
      />
      <div style="display:flex;gap:8px;margin-top:8px">
        <button class="btn" @click="useDefault">{{ t('rename.useDefaultTemplate') }}</button>
      </div>
      <div style="margin-top:12px">
        <span class="eyebrow">{{ t('naming.insertPlaceholder') }}</span>
        <div class="pill-row" style="margin-top:6px">
          <button
            v-for="tk in tokens"
            :key="tk.token"
            class="chip"
            @click="insertPlaceholder(tk.token)"
          >
            {{ tk.token }}
          </button>
        </div>
      </div>
    </div>

    <div class="preview-sample" style="margin-top:14px">
      <div class="sample-thumb"></div>
      <div>
        <span class="eyebrow" style="color:rgba(255,255,255,0.6)">{{ t('naming.livePreview') }}</span>
        <div class="mono" style="color:#fff;margin-top:4px;font-size:13px">{{ liveSample }}.ARW</div>
      </div>
    </div>

    <div v-if="error" class="alert alert-error" style="margin-top:14px">{{ error }}</div>

    <div style="margin-top:16px">
      <button class="btn primary" :disabled="loading || !projectRoot" @click="generatePlan">
        {{ loading ? t('naming.generating') : t('naming.generatePlan') }}
      </button>
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

.template-box { display: grid; gap: 4px; }

.chip {
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--panel);
  color: var(--accent);
  padding: 6px 10px;
  font-family: "SF Mono", Menlo, Consolas, monospace;
  font-size: 12px;
  font-weight: 720;
  cursor: pointer;
}

.chip:hover {
  border-color: var(--accent);
  background: var(--accent-soft);
}

.preview-sample {
  display: grid;
  grid-template-columns: 70px minmax(0, 1fr);
  gap: 10px;
  align-items: center;
  border-radius: 12px;
  background: var(--preview);
  padding: 14px;
}

.sample-thumb {
  aspect-ratio: 1.2;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0)), var(--preview-thumb);
}
</style>
