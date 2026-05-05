<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useJourney } from '../composables/useJourney'
import ThemeSwitcher from '../components/ThemeSwitcher.vue'
import { setLocale } from '@/i18n'

const { t, locale } = useI18n()
const { theme } = useJourney()

function changeLanguage(event: Event) {
  const target = event.target as HTMLSelectElement
  if (['zh', 'en'].includes(target.value)) {
    setLocale(target.value as 'zh' | 'en')
  }
}
</script>

<template>
  <div class="utility-page">
    <div class="utility-header">
      <span class="eyebrow">{{ t('journey.utilityPage') }}</span>
      <h3>{{ t('settings.title') }}</h3>
      <p>{{ t('settings.description') }}</p>
    </div>

    <div class="panel-card panel-pad">
      <div class="settings-group">
        <h4>{{ t('settings.general') }}</h4>
        <div class="setting-row">
          <div>
            <strong>{{ t('settings.language') }}</strong>
          </div>
          <select class="input" style="width:auto" :value="locale" @change="changeLanguage">
            <option value="zh">中文</option>
            <option value="en">English</option>
          </select>
        </div>
        <div class="setting-row">
          <div>
            <strong>{{ t('settings.theme') }}</strong>
            <span>{{ t('settings.theme') }}</span>
          </div>
          <span class="setting-value">{{ theme }}</span>
        </div>
        <ThemeSwitcher />
      </div>

      <div class="settings-group">
        <h4>{{ t('settings.workflowDefaults') }}</h4>
        <div class="setting-row">
          <div>
            <strong>{{ t('settings.namingTemplate') }}</strong>
          </div>
          <span class="setting-value locked">{{ '{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}' }}</span>
        </div>
        <div class="setting-row">
          <div>
            <strong>{{ t('settings.postProcessor') }}</strong>
          </div>
          <span class="setting-value">Lightroom</span>
        </div>
        <div class="setting-row">
          <div>
            <strong>{{ t('settings.sidecarPolicy') }}</strong>
          </div>
          <span class="setting-value">{{ t('settings.sameStem') }}</span>
        </div>
      </div>

      <div class="settings-group">
        <h4>{{ t('settings.archiveGroup') }}</h4>
        <div class="setting-row">
          <div>
            <strong>{{ t('settings.archiveNaming') }}</strong>
          </div>
          <span class="setting-value">{{ t('settings.timestamp') }}</span>
        </div>
        <div class="setting-row">
          <div>
            <strong>{{ t('settings.excludeRules') }}</strong>
          </div>
          <span class="setting-value">{{ t('settings.defaultRules') }}</span>
        </div>
      </div>

      <div class="settings-group">
        <h4>{{ t('settings.securityRules') }}</h4>
        <div class="setting-row">
          <div>
            <strong>{{ t('settings.dryRunRequired') }}</strong>
          </div>
          <span class="setting-value locked">{{ t('settings.alwaysOn') }}</span>
        </div>
        <div class="setting-row">
          <div>
            <strong>{{ t('settings.originalNameImmutable') }}</strong>
          </div>
          <span class="setting-value locked">{{ t('settings.immutable') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.utility-page {
  display: grid;
  gap: 14px;
}

.utility-header {
  border: 1px solid var(--accent-line);
  border-radius: var(--radius);
  background: var(--accent-soft);
  padding: 16px;
}

.utility-header h3 {
  margin: 2px 0 0;
  font-size: 22px;
}

.utility-header p {
  margin: 6px 0 0;
  color: var(--muted);
  font-size: 13px;
}

.settings-group {
  padding: 14px 0;
  border-bottom: 1px solid var(--line);
}

.settings-group:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.settings-group h4 {
  margin: 0 0 10px;
  font-size: 13px;
}

.setting-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  padding: 8px 0;
}

.setting-row strong { display: block; font-size: 13px; }

.setting-row span {
  display: block;
  margin-top: 2px;
  color: var(--muted);
  font-size: 12px;
}

.setting-value {
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--panel-soft);
  color: var(--ink);
  padding: 6px 9px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.setting-value.locked { color: var(--accent); }
</style>
