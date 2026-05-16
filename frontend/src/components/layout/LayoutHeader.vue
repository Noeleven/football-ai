<template>
  <header class="header">
    <div class="header-content">
      <div class="logo" @click="router.push('/')">
        <span class="logo-icon">⚽</span>
        <span class="logo-text">{{ t('app.name') }}</span>
      </div>

      <nav class="nav">
        <router-link to="/" class="nav-item">{{ t('nav.home') }}</router-link>
        <router-link to="/news" class="nav-item">{{ t('nav.news') }}</router-link>
        <router-link to="/teams" class="nav-item">{{ t('nav.teams') }}</router-link>
        <router-link to="/matches" class="nav-item">{{ t('nav.matches') }}</router-link>
        <router-link to="/admin" class="nav-item admin-link" v-if="isAdmin">{{ t('nav.admin') }}</router-link>
      </nav>

      <div class="header-actions">
        <el-dropdown @command="handleLanguageChange">
          <span class="language-switch">
            <el-icon><Globe /></el-icon>
            {{ currentLanguage }}
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="zh-CN">中文</el-dropdown-item>
              <el-dropdown-item command="en">English</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Globe } from '@element-plus/icons-vue'

const router = useRouter()
const { t, locale } = useI18n()

const isAdmin = computed(() => {
  return router.currentRoute.value.path.startsWith('/admin')
})

const currentLanguage = computed(() => {
  return locale.value === 'zh-CN' ? '中文' : 'EN'
})

const handleLanguageChange = (lang: string) => {
  locale.value = lang
  localStorage.setItem('locale', lang)
}
</script>

<style scoped>
.header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.logo-icon {
  font-size: 28px;
  margin-right: 8px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #409eff;
}

.nav {
  display: flex;
  gap: 30px;
}

.nav-item {
  font-size: 15px;
  color: #606266;
  transition: color 0.3s;
}

.nav-item:hover,
.nav-item.router-link-active {
  color: #409eff;
}

.admin-link {
  color: #e6a23c;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.language-switch {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  color: #606266;
  font-size: 14px;
}
</style>