<template>
  <div class="matches-view page-container">
    <h1 class="page-title">{{ t('matches.title') }}</h1>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" @tab-change="loadMatches">
      <el-tab-pane label="Upcoming" name="upcoming" />
      <el-tab-pane label="Recent" name="recent" />
    </el-tabs>

    <!-- Competition Filter -->
    <div class="filters">
      <el-select v-model="selectedCompetition" placeholder="All Competitions" @change="loadMatches" clearable>
        <el-option label="All" value="" />
        <el-option v-for="comp in competitions" :key="comp.id" :label="comp.name" :value="comp.id" />
      </el-select>
    </div>

    <!-- Matches Grid -->
    <div class="matches-grid" v-loading="loading">
      <MatchCard v-for="match in matches" :key="match.match_id" :match="match" />
    </div>

    <div v-if="!loading && matches.length === 0" class="no-data">
      No matches found
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { getUpcomingMatches, getRecentMatches, getCompetitions } from '@/services/api'
import MatchCard from '@/components/common/MatchCard.vue'

const { t } = useI18n()

const matches = ref<any[]>([])
const loading = ref(false)
const activeTab = ref('upcoming')
const selectedCompetition = ref('')
const competitions = ref<any[]>([])

const loadMatches = async () => {
  loading.value = true
  try {
    const res = activeTab.value === 'upcoming'
      ? await getUpcomingMatches(selectedCompetition.value)
      : await getRecentMatches(selectedCompetition.value)
    matches.value = res.data || []
  } catch (error) {
    console.error('Failed to load matches:', error)
  } finally {
    loading.value = false
  }
}

const loadCompetitions = async () => {
  try {
    const res = await getCompetitions()
    competitions.value = res.data || []
  } catch (error) {
    console.error('Failed to load competitions:', error)
  }
}

onMounted(() => {
  loadMatches()
  loadCompetitions()
})
</script>

<style scoped>
.matches-view {
  max-width: 1200px;
  margin: 0 auto;
}

.filters {
  margin: 20px 0;
}

.matches-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.no-data {
  text-align: center;
  padding: 60px;
  color: #909399;
}
</style>