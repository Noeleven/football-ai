<template>
  <div class="admin-view">
    <el-container>
      <el-aside width="200px">
        <el-menu :default-active="activeMenu" router>
          <el-menu-item index="/admin/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <span>{{ t('admin.dashboard') }}</span>
          </el-menu-item>
          <el-sub-menu index="data">
            <template #title>
              <el-icon><Management /></el-icon>
              <span>{{ t('admin.data_management') }}</span>
            </template>
            <el-menu-item index="/admin/teams">{{ t('nav.teams') }}</el-menu-item>
            <el-menu-item index="/admin/players">{{ t('nav.players') }}</el-menu-item>
            <el-menu-item index="/admin/matches">{{ t('nav.matches') }}</el-menu-item>
            <el-menu-item index="/admin/news">{{ t('nav.news') }}</el-menu-item>
          </el-sub-menu>
          <el-menu-item index="/admin/settings">
            <el-icon><Setting /></el-icon>
            <span>{{ t('admin.system_settings') }}</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { DataAnalysis, Management, Setting } from '@element-plus/icons-vue'

const { t } = useI18n()
const route = useRoute()

const activeMenu = computed(() => route.path)
</script>

<style scoped>
.admin-view {
  height: 100vh;
}

.el-container {
  height: 100%;
}

.el-aside {
  background: #f5f7fa;
  border-right: 1px solid #e4e7ed;
}

.el-main {
  background: #fff;
  padding: 20px;
}
</style>