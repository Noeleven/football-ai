<template>
  <div class="news-view page-container">
    <h1 class="page-title">{{ t('news.title') }}</h1>

    <!-- Filters -->
    <div class="filters">
      <el-radio-group v-model="selectedType" @change="loadNews">
        <el-radio-button value="">{{ t('news.types.all') }}</el-radio-button>
        <el-radio-button value="transfer">{{ t('news.types.transfer') }}</el-radio-button>
        <el-radio-button value="injury">{{ t('news.types.injury') }}</el-radio-button>
        <el-radio-button value="schedule">{{ t('news.types.schedule') }}</el-radio-button>
        <el-radio-button value="general">{{ t('news.types.general') }}</el-radio-button>
      </el-radio-group>
    </div>

    <!-- News List -->
    <div class="news-list" v-loading="loading">
      <NewsItem v-for="news in newsList" :key="news.news_id" :news="news" />
      <div v-if="!loading && newsList.length === 0" class="no-data">
        {{ t('news.no_news') }}
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        @current-change="loadNews"
        layout="prev, pager, next"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { getNews } from '@/services/api'
import NewsItem from '@/components/common/NewsItem.vue'

const { t } = useI18n()

const newsList = ref<any[]>([])
const loading = ref(false)
const selectedType = ref('')
const currentPage = ref(1)
const pageSize = 20
const total = ref(0)

const loadNews = async () => {
  loading.value = true
  try {
    const res = await getNews(selectedType.value, '', pageSize)
    newsList.value = res.data || []
    total.value = res.total || 0
  } catch (error) {
    console.error('Failed to load news:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadNews()
})
</script>

<style scoped>
.news-view {
  max-width: 900px;
  margin: 0 auto;
}

.filters {
  margin-bottom: 20px;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.no-data {
  text-align: center;
  padding: 60px;
  color: #909399;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}
</style>