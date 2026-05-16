<template>
  <footer class="footer">
    <div class="footer-content">
      <p>&copy; 2024 Football AI Platform. All rights reserved.</p>
      <p>{{ t('app.name') }} - AI-powered football analysis</p>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
</script>

<style scoped>
.footer {
  background: #f5f7fa;
  border-top: 1px solid #e4e7ed;
  padding: 20px;
  margin-top: 40px;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  text-align: center;
  color: #909399;
  font-size: 14px;
}
</style>