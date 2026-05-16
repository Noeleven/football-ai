<template>
  <div class="prediction-card" @click="goToMatch">
    <div class="card-header">
      <span class="match-time">{{ formatTime(prediction.match_time) }}</span>
      <span class="confidence" :class="prediction.confidence_level">{{ prediction.confidence_level }}</span>
    </div>
    <div class="match-teams">
      <span class="team">{{ prediction.home_team_name }}</span>
      <span class="score-pred">{{ prediction.score_prediction?.home_goals }} - {{ prediction.score_prediction?.away_goals }}</span>
      <span class="team">{{ prediction.away_team_name }}</span>
    </div>
    <div class="win-probs">
      <div class="prob" v-for="wp in prediction.win_probabilities" :key="wp.outcome">
        <span class="label">{{ getOutcomeLabel(wp.outcome) }}</span>
        <el-progress :percentage="Math.round(wp.probability * 100)" :stroke-width="8" />
      </div>
    </div>
    <div class="recommendation">
      <span class="rec-label">推荐:</span>
      <span class="rec-value">{{ getRecommendationLabel(prediction.recommendation) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'

const props = defineProps<{
  prediction: {
    prediction_id: string
    match_id: string
    home_team_name: string
    away_team_name: string
    match_time: string
    score_prediction?: { home_goals: number; away_goals: number }
    win_probabilities: Array<{ outcome: string; probability: number }>
    recommendation: string
    confidence_level: string
  }
}>()

const router = useRouter()

const formatTime = (time: string) => {
  return dayjs(time).format('MM/DD HH:mm')
}

const getOutcomeLabel = (outcome: string) => {
  const labels: Record<string, string> = {
    home_win: '主胜',
    draw: '平局',
    away_win: '客胜',
  }
  return labels[outcome] || outcome
}

const getRecommendationLabel = (rec: string) => {
  const labels: Record<string, string> = {
    strong_home: '强烈主胜',
    home: '主胜',
    draw: '平局',
    away: '客胜',
    strong_away: '强烈客胜',
  }
  return labels[rec] || rec
}

const goToMatch = () => {
  router.push(`/matches/${props.prediction.match_id}`)
}
</script>

<style scoped>
.prediction-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.prediction-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.match-time {
  font-size: 14px;
  color: #909399;
}

.confidence {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
}

.confidence.high { background: #67c23a; color: #fff; }
.confidence.medium { background: #e6a23c; color: #fff; }
.confidence.low { background: #909399; color: #fff; }

.match-teams {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.team {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.score-pred {
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
}

.win-probs {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 15px;
}

.prob {
  display: flex;
  align-items: center;
  gap: 10px;
}

.label {
  font-size: 12px;
  color: #606266;
  min-width: 40px;
}

.recommendation {
  display: flex;
  gap: 8px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.rec-label {
  font-size: 14px;
  color: #909399;
}

.rec-value {
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
}
</style>