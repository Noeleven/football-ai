<template>
  <div class="player-detail-view page-container" v-loading="loading">
    <div class="player-header card" v-if="player">
      <div class="player-avatar">{{ getPositionEmoji(player.position) }}</div>
      <div class="player-info">
        <h1 class="player-name">{{ player.name }}</h1>
        <p class="player-name-cn">{{ player.name_cn }}</p>
        <div class="player-meta">
          <span>{{ player.position }}</span>
          <span>{{ player.nationality }}</span>
          <span v-if="player.birth_date">Age: {{ calculateAge(player.birth_date) }}</span>
        </div>
      </div>
      <div class="player-value">{{ player.market_value }}M</div>
    </div>

    <!-- Stats -->
    <div class="card" v-if="player?.current_stats">
      <h3 class="card-title">{{ t('players.stats') }}</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-value">{{ player.current_stats.goals }}</span>
          <span class="stat-label">Goals</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ player.current_stats.assists }}</span>
          <span class="stat-label">Assists</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ player.current_stats.appearances }}</span>
          <span class="stat-label">Appearances</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ player.current_stats.pass_accuracy }}%</span>
          <span class="stat-label">Pass Accuracy</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ player.current_stats.tackles }}</span>
          <span class="stat-label">Tackles</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ player.current_stats.rating }}</span>
          <span class="stat-label">Rating</span>
        </div>
      </div>
    </div>

    <!-- Injury Status -->
    <div class="card" v-if="player">
      <h3 class="card-title">{{ t('players.injury_status') }}</h3>
      <el-tag :type="player.injury_status === 'fit' ? 'success' : 'danger'">
        {{ player.injury_status === 'fit' ? 'Fit' : player.injury_status }}
      </el-tag>
    </div>

    <!-- Strengths & Weaknesses -->
    <div class="card" v-if="player">
      <h3 class="card-title">Strengths</h3>
      <div class="tags">
        <el-tag v-for="s in player.strengths" :key="s" type="success">{{ s }}</el-tag>
      </div>
      <h3 class="card-title" style="margin-top: 20px">Weaknesses</h3>
      <div class="tags">
        <el-tag v-for="w in player.weaknesses" :key="w" type="warning">{{ w }}</el-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getTeam, searchPlayers } from '@/services/api'

const { t } = useI18n()
const route = useRoute()

const player = ref<any>(null)
const loading = ref(false)

const getPositionEmoji = (position: string) => {
  const emojis: Record<string, string> = { GK: '🧤', DF: '🛡️', MF: '⚙️', FW: '⚽' }
  return emojis[position] || '⚽'
}

const calculateAge = (birthDate: string) => {
  const birth = new Date(birthDate)
  const today = new Date()
  let age = today.getFullYear() - birth.getFullYear()
  const m = today.getMonth() - birth.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--
  return age
}

const loadPlayer = async () => {
  loading.value = true
  try {
    const playerId = route.params.id as string
    // In real app, would have getPlayer API
    const res = await searchPlayers(playerId)
    player.value = res.data?.[0] || null
  } catch (error) {
    console.error('Failed to load player:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPlayer()
})
</script>

<style scoped>
.player-detail-view {
  max-width: 900px;
  margin: 0 auto;
}

.player-header {
  display: flex;
  align-items: center;
  gap: 30px;
}

.player-avatar {
  font-size: 72px;
}

.player-name {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.player-name-cn {
  font-size: 18px;
  color: #606266;
  margin: 5px 0;
}

.player-meta {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #909399;
}

.player-value {
  font-size: 32px;
  font-weight: 700;
  color: #409eff;
  margin-left: auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #409eff;
  display: block;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
</style>