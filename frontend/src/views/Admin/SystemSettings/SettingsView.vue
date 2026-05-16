<template>
  <div class="settings-view">
    <h1>{{ t('admin.system_settings') }}</h1>

    <div class="card">
      <h3 class="card-title">Application Settings</h3>
      <el-form label-width="150px">
        <el-form-item label="App Name">
          <el-input v-model="settings.appName" />
        </el-form-item>
        <el-form-item label="Debug Mode">
          <el-switch v-model="settings.debug" />
        </el-form-item>
        <el-form-item label="Log Level">
          <el-select v-model="settings.logLevel">
            <el-option label="DEBUG" value="DEBUG" />
            <el-option label="INFO" value="INFO" />
            <el-option label="WARN" value="WARN" />
            <el-option label="ERROR" value="ERROR" />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <div class="card">
      <h3 class="card-title">LLM Settings</h3>
      <el-form label-width="150px">
        <el-form-item label="Provider">
          <el-select v-model="settings.llmProvider">
            <el-option label="Gemini" value="gemini" />
            <el-option label="OpenAI" value="openai" />
          </el-select>
        </el-form-item>
        <el-form-item label="Gemini API Key">
          <el-input v-model="settings.geminiApiKey" type="password" show-password />
        </el-form-item>
        <el-form-item label="Gemini Model">
          <el-input v-model="settings.geminiModel" />
        </el-form-item>
      </el-form>
    </div>

    <div class="card">
      <h3 class="card-title">Cache Settings</h3>
      <el-form label-width="150px">
        <el-form-item label="Enable Cache">
          <el-switch v-model="settings.cacheEnabled" />
        </el-form-item>
        <el-form-item label="Cache TTL (seconds)">
          <el-input-number v-model="settings.cacheTtl" :min="60" :max="86400" />
        </el-form-item>
      </el-form>
    </div>

    <div class="actions">
      <el-button type="primary" @click="saveSettings">{{ t('common.save') }}</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const settings = ref({
  appName: 'Football AI Platform',
  debug: false,
  logLevel: 'INFO',
  llmProvider: 'gemini',
  geminiApiKey: '',
  geminiModel: 'gemini-2.0-flash',
  cacheEnabled: true,
  cacheTtl: 3600,
})

const saveSettings = () => {
  console.log('Save settings:', settings.value)
}
</script>

<style scoped>
.settings-view {
  max-width: 800px;
}

.actions {
  margin-top: 30px;
  text-align: right;
}
</style>