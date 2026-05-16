<template>
  <div id="app">
    <el-config-provider :locale="locale">
      <LayoutHeader />
      <main class="main-content">
        <router-view />
      </main>
      <LayoutFooter />
    </el-config-provider>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import LayoutHeader from '@/components/layout/LayoutHeader.vue'
import LayoutFooter from '@/components/layout/LayoutFooter.vue'

const { locale } = useI18n()

const currentLocale = computed(() => {
  return locale.value === 'zh-CN' ? zhCN : en
})
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}
</style>

<script lang="ts">
import zhCN from 'element-plus/dist/locale/zh-cn.mjs'
import en from 'element-plus/dist/locale/en.mjs'

export default {
  data() {
    return {
      locale: zhCN,
    }
  },
  watch: {
    '$i18n.locale': function(newLocale: string) {
      this.locale = newLocale === 'zh-CN' ? zhCN : en
    },
  },
}
</script>