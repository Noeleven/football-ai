<template>
  <div class="home-view">
    <!-- Hero Section -->
    <section class="hero-section">
      <h1>{{ t('home.title') }}</h1>
      <p>{{ t('app.welcome') }}</p>
    </section>

    <!-- Upcoming Matches -->
    <section class="section">
      <div class="section-header">
        <h2>{{ t('home.upcoming_matches') }}</h2>
        <router-link to="/matches" class="view-all">{{ t('home.view_all') }}</router-link>
      </div>
      <div class="matches-grid">
        <MatchCard v-for="match in upcomingMatches" :key="match.match_id" :match="match" />
      </div>
      <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    </section>

    <!-- Hot News -->
    <section class="section">
      <div class="section-header">
        <h2>{{ t('home.hot_news') }}</h2>
        <router-link to="/news" class="view-all">{{ t('home.view_all') }}</router-link>
      </div>
      <div class="news-list">
        <NewsItem v-for="news in hotNews" :key="news.news_id" :news="news" />
      </div>
    </section>

    <!-- AI Predictions -->
    <section class="section">
      <div class="section-header">
        <h2>{{ t('home.ai_predictions') }}</h2>
      </div>
      <div class="predictions-grid">
        <PredictionCard v-for="pred in predictions" :key="pred.prediction_id" :prediction="pred" />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { getUpcomingMatches, getRecentNews, getRecentPredictions } from '@/services/api'
import MatchCard from '@/components/common/MatchCard.vue'
import NewsItem from '@/components/common/NewsItem.vue'
import PredictionCard from '@/components/common/PredictionCard.vue'

const { t } = useI18n()

const upcomingMatches = ref<any[]>([])
const hotNews = ref<any[]>([])
const predictions = ref<any[]>([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const [matchesRes, newsRes, predsRes] = await Promise.all([
      getUpcomingMatches(),
      getRecentNews(),
      getRecentPredictions(),
    ])
    upcomingMatches.value = matchesRes.data || []
    hotNews.value = (newsRes.data || []).slice(0, 5)
    predictions.value = (predsRes.data || []).slice(0, 4)
  } catch (error) {
    console.error('Failed to load home data:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.home-view {
  max-width: 1200px;
  margin: 0 auto;
}

.hero-section {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: #fff;
  padding: 60px 40px;
  border-radius: 12px;
  text-align: center;
  margin-bottom: 40px;
}

.hero-section h1 {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 10px;
}

.hero-section p {
  font-size: 18px;
  opacity: 0.9;
}

.section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.view-all {
  color: #409eff;
  font-size: 14px;
}

.matches-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.predictions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #909399;
}
</style>