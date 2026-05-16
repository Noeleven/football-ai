<template>
  <div class="match-detail-view page-container" v-loading="loading">
    <!-- Match Header -->
    <div class="match-header card" v-if="match">
      <div class="match-time">{{ formatTime(match.match_time) }}</div>
      <div class="match-teams">
        <div class="team home">
          <div class="team-logo">{{ getTeamEmoji(match.home_team_name) }}</div>
          <div class="team-name">{{ match.home_team_name }}</div>
        </div>
        <div class="score-box">
          <span v-if="match.status === 'finished'" class="score">{{ match.home_score }} - {{ match.away_score }}</span>
          <span v-else class="vs">VS</span>
          <div class="match-status">{{ getStatusLabel(match.status) }}</div>
        </div>
        <div class="team away">
          <div class="team-logo">{{ getTeamEmoji(match.away_team_name) }}</div>
          <div class="team-name">{{ match.away_team_name }}</div>
        </div>
      </div>
      <div class="match-info">
        <span>{{ match.competition_name }}</span>
        <span>{{ match.round }}</span>
        <span>{{ match.venue }}</span>
      </div>
    </div>

    <!-- AI Prediction -->
    <div class="card" v-if="prediction">
      <h3 class="card-title">{{ t('matches.prediction.title') }}</h3>
      <div class="prediction-content">
        <div class="predicted-score">
          <span class="label">{{ t('matches.prediction.score') }}:</span>
          <span class="value">{{ prediction.score_prediction?.home_goals }} - {{ prediction.score_prediction?.away_goals }}</span>
          <el-tag :type="getConfidenceType(prediction.confidence_level)" size="small">
            {{ prediction.confidence_level }} confidence
          </el-tag>
        </div>

        <!-- Win Probabilities -->
        <div class="win-probs">
          <h4>{{ t('matches.prediction.win_probability') }}</h4>
          <WinRatePie :data="winProbData" />
        </div>

        <!-- Formation -->
        <div class="formation-info">
          <div>
            <span class="label">Home Formation:</span>
            <span class="value">{{ prediction.predicted_formation_home }}</span>
          </div>
          <div>
            <span class="label">Away Formation:</span>
            <span class="value">{{ prediction.predicted_formation_away }}</span>
          </div>
        </div>

        <!-- Key Factors -->
        <div class="key-factors" v-if="prediction.key_factors?.length">
          <h4>Key Factors:</h4>
          <ul>
            <li v-for="f in prediction.key_factors" :key="f">{{ f }}</li>
          </ul>
        </div>

        <!-- Report -->
        <div class="report-markdown" v-if="prediction.report_markdown" v-html="prediction.report_markdown" />
      </div>
    </div>

    <!-- Post Match Analysis -->
    <div class="card" v-if="analysis">
      <h3 class="card-title">{{ t('matches.post_match.title') }}</h3>
      <div class="analysis-content">
        <p><strong>Accuracy:</strong> {{ analysis.prediction_accuracy }}</p>
        <p><strong>{{ t('matches.post_match.events') }}:</strong> {{ analysis.match_events_summary }}</p>
        <p><strong>{{ t('matches.post_match.tactical') }}:</strong> {{ analysis.tactical_summary }}</p>
        <p><strong>{{ t('matches.post_match.key_performers') }}:</strong> {{ analysis.key_performers?.join(', ') }}</p>
        <div v-if="analysis.report_markdown" v-html="analysis.report_markdown" />
      </div>
    </div>

    <!-- Generate Prediction Button -->
    <div class="actions" v-if="match && !prediction">
      <el-button type="primary" @click="generatePrediction" :loading="predicting">
        Generate AI Prediction
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getMatch, predictMatch, analyzeMatch } from '@/services/api'
import WinRatePie from '@/components/chart/WinRatePie.vue'

const { t } = useI18n()
const route = useRoute()

const match = ref<any>(null)
const prediction = ref<any>(null)
const analysis = ref<any>(null)
const loading = ref(false)
const predicting = ref(false)

const getTeamEmoji = (name: string) => {
  const emojis: Record<string, string> = {
    'Argentina': '🇦🇷', 'Brazil': '🇧🇷', 'France': '🇫🇷', 'Germany': '🇩🇪',
    'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Spain': '🇪🇸', 'Italy': '🇮🇹',
  }
  return emojis[name] || '⚽'
}

const formatTime = (time: string) => new Date(time).toLocaleString()

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    scheduled: 'Scheduled', live: 'Live', halftime: 'Halftime',
    finished: 'Finished', postponed: 'Postponed', cancelled: 'Cancelled',
  }
  return labels[status] || status
}

const getConfidenceType = (level: string) => {
  const types: Record<string, string> = { high: 'success', medium: 'warning', low: 'info' }
  return types[level] || 'info'
}

const winProbData = computed(() => {
  if (!prediction.value?.win_probabilities) return []
  return prediction.value.win_probabilities.map((wp: any) => ({
    name: wp.outcome === 'home_win' ? 'Home Win' : wp.outcome === 'draw' ? 'Draw' : 'Away Win',
    value: wp.probability,
  }))
})

const loadMatch = async () => {
  loading.value = true
  try {
    const matchId = route.params.id as string
    const res = await getMatch(matchId)
    match.value = res.data
  } catch (error) {
    console.error('Failed to load match:', error)
  } finally {
    loading.value = false
  }
}

const generatePrediction = async () => {
  predicting.value = true
  try {
    const matchId = route.params.id as string
    const res = await predictMatch(matchId)
    prediction.value = res.data
  } catch (error) {
    console.error('Failed to generate prediction:', error)
  } finally {
    predicting.value = false
  }
}

onMounted(() => {
  loadMatch()
})
</script>

<style scoped>
.match-detail-view {
  max-width: 900px;
  margin: 0 auto;
}

.match-header {
  text-align: center;
}

.match-time {
  color: #909399;
  font-size: 14px;
  margin-bottom: 20px;
}

.match-teams {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 40px;
  margin-bottom: 20px;
}

.team {
  text-align: center;
}

.team-logo {
  font-size: 48px;
  margin-bottom: 10px;
}

.team-name {
  font-size: 18px;
  font-weight: 600;
}

.score-box {
  text-align: center;
}

.score {
  font-size: 48px;
  font-weight: 700;
  color: #409eff;
}

.vs {
  font-size: 32px;
  color: #909399;
}

.match-status {
  font-size: 12px;
  color: #67c23a;
  margin-top: 5px;
}

.match-info {
  display: flex;
  justify-content: center;
  gap: 15px;
  color: #909399;
  font-size: 14px;
}

.prediction-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.predicted-score {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 24px;
}

.predicted-score .label {
  font-weight: 600;
}

.predicted-score .value {
  color: #409eff;
  font-weight: 700;
}

.win-probs {
  margin-top: 20px;
}

.formation-info {
  display: flex;
  gap: 40px;
}

.formation-info .label {
  color: #909399;
  font-size: 14px;
}

.formation-info .value {
  font-weight: 600;
  margin-left: 5px;
}

.key-factors ul {
  padding-left: 20px;
}

.key-factors li {
  margin: 5px 0;
  color: #606266;
}

.report-markdown, .analysis-content {
  margin-top: 20px;
  line-height: 1.6;
}

.actions {
  text-align: center;
  margin-top: 30px;
}
</style>