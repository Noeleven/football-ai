<template>
  <div class="news-item" @click="goToNews">
    <div class="news-meta">
      <span class="news-type" :class="news.news_type">{{ getTypeLabel(news.news_type) }}</span>
      <span class="news-time">{{ formatTime(news.published_at) }}</span>
    </div>
    <h3 class="news-title">{{ news.title }}</h3>
    <p class="news-summary" v-if="news.summary">{{ news.summary }}</p>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import dayjs from 'dayjs'

const props = defineProps<{
  news: {
    news_id: string
    title: string
    summary?: string
    news_type: string
    published_at: string
  }
}>()

const { t } = useI18n()

const formatTime = (time: string) => {
  return dayjs(time).format('MM/DD HH:mm')
}

const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    transfer: t('news.types.transfer'),
    injury: t('news.types.injury'),
    schedule: t('news.types.schedule'),
    general: t('news.types.general'),
  }
  return labels[type] || type
}

const goToNews = () => {
  // Could navigate to detail page
}
</script>

<style scoped>
.news-item {
  background: #fff;
  border-radius: 8px;
  padding: 16px 20px;
  cursor: pointer;
  transition: background 0.2s;
}

.news-item:hover {
  background: #f5f7fa;
}

.news-meta {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
}

.news-type {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #409eff;
  color: #fff;
}

.news-type.transfer { background: #67c23a; }
.news-type.injury { background: #f56c6c; }
.news-type.schedule { background: #e6a23c; }

.news-time {
  font-size: 12px;
  color: #909399;
}

.news-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
  line-height: 1.4;
}

.news-summary {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
</style>