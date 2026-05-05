<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="utility-page">
    <div class="utility-header">
      <span class="eyebrow">{{ t('journey.utilityPage') }}</span>
      <h3>{{ t('safety.title') }}</h3>
      <p>{{ t('safety.description') }}</p>
    </div>

    <div class="panel-card panel-pad">
      <div class="settings-group">
        <h4>{{ t('safety.executionProtection') }}</h4>
        <div class="setting-row">
          <div>
            <strong>{{ t('safety.dryRunEnforced') }}</strong>
            <span>{{ t('safety.dryRunEnforcedDesc') }}</span>
          </div>
          <span class="setting-value locked">{{ t('safety.mandatory') }}</span>
        </div>
        <div class="setting-row">
          <div>
            <strong>{{ t('safety.blockingErrors') }}</strong>
            <span>{{ t('safety.blockingErrorsDesc') }}</span>
          </div>
          <span class="setting-value">0</span>
        </div>
      </div>

      <div class="settings-group">
        <h4>{{ t('safety.traceability') }}</h4>
        <div class="setting-row">
          <div>
            <strong>{{ t('safety.originalNameProtected') }}</strong>
            <span>{{ t('safety.originalNameProtectedDesc') }}</span>
          </div>
          <span class="setting-value locked">{{ t('safety.protected') }}</span>
        </div>
        <div class="setting-row">
          <div>
            <strong>{{ t('safety.sidecarSync') }}</strong>
            <span>{{ t('safety.sidecarSyncDesc') }}</span>
          </div>
          <span class="setting-value">{{ t('safety.sameStemOnly') }}</span>
        </div>
      </div>

      <div class="settings-group">
        <h4>{{ t('safety.authorization') }}</h4>
        <div class="setting-row">
          <div>
            <strong>{{ t('safety.directoryAuthorization') }}</strong>
            <span>{{ t('safety.directoryAuthorizationDesc') }}</span>
          </div>
          <span class="setting-value locked">{{ t('safety.authorized') }}</span>
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
