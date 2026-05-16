<template>
  <div class="team-detail-view page-container" v-loading="loading">
    <!-- Team Header -->
    <div class="team-header card" v-if="team">
      <div class="team-info">
        <div class="team-logo">{{ getTeamEmoji(team.name) }}</div>
        <div class="team-meta">
          <h1 class="team-name">{{ team.name }}</h1>
          <p class="team-name-cn">{{ team.name_cn }}</p>
          <p class="team-country">{{ team.country }} | {{ team.stadium }}</p>
          <p class="team-founded" v-if="team.founded_year">Founded: {{ team.founded_year }}</p>
        </div>
      </div>
      <div class="team-stats-summary">
        <div class="stat">
          <span class="stat-value">{{ team.total_market_value?.toFixed(0) || 'N/A' }}</span>
          <span class="stat-label">Market Value (M)</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ team.squad_size || 'N/A' }}</span>
          <span class="stat-label">Squad Size</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ team.avg_player_age || 'N/A' }}</span>
          <span class="stat-label">Avg Age</span>
        </div>
      </div>
    </div>

    <!-- Team Stats Chart -->
    <div class="card" v-if="team?.stats">
      <h3 class="card-title">{{ t('teams.stats') }}</h3>
      <div class="stats-grid">
        <StatsChart :data="statsData" type="bar" />
      </div>
    </div>

    <!-- Key Players -->
    <div class="card">
      <h3 class="card-title">{{ t('teams.key_players') }}</h3>
      <div class="players-grid">
        <div v-for="player in keyPlayers" :key="player.player_id" class="player-item" @click="goToPlayer(player.player_id)">
          <div class="player-name">{{ player.name }}</div>
          <div class="player-position">{{ player.position }}</div>
          <div class="player-value">{{ player.market_value }}M</div>
        </div>
      </div>
    </div>

    <!-- Recent Matches -->
    <div class="card">
      <h3 class="card-title">Recent Matches</h3>
      <div class="matches-list">
        <div v-for="match in recentMatches" :key="match.match_id" class="match-item" @click="goToMatch(match.match_id)">
          <span class="match-teams">{{ match.home_team_name }} vs {{ match.away_team_name }}</span>
          <span class="match-score" v-if="match.status === 'finished'">{{ match.home_score }} - {{ match.away_score }}</span>
          <span class="match-time">{{ formatTime(match.match_time) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getTeam, getKeyPlayers, getRecentMatches } from '@/services/api'
import StatsChart from '@/components/chart/StatsChart.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const team = ref<any>(null)
const keyPlayers = ref<any[]>([])
const recentMatches = ref<any[]>([])
const loading = ref(false)

const getTeamEmoji = (name: string) => {
  const emojis: Record<string, string> = {
    'Argentina': '🇦🇷', 'Brazil': '🇧🇷', 'France': '🇫🇷', 'Germany': '🇩🇪',
    'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Spain': '🇪🇸', 'Italy': '🇮🇹',
  }
  return emojis[name] || '⚽'
}

const statsData = computed(() => {
  if (!team.value?.stats) return { labels: [], values: [] }
  const stats = team.value.stats
  return {
    title: 'Team Statistics',
    labels: ['Possession', 'Shots', 'Pass Accuracy', 'Win Rate'],
    values: [
      stats.avg_possession || 0,
      stats.avg_shots_per_game || 0,
      stats.pass_accuracy || 0,
      (stats.win_rate || 0) * 100,
    ],
    color: '#409eff',
  }
})

const formatTime = (time: string) => {
  return new Date(time).toLocaleDateString()
}

const loadTeam = async () => {
  loading.value = true
  try {
    const teamId = route.params.id as string
    const [teamRes, playersRes, matchesRes] = await Promise.all([
      getTeam(teamId),
      getKeyPlayers(teamId),
      getRecentMatches('', 10),
    ])
    team.value = teamRes.data
    keyPlayers.value = (playersRes.data || []).slice(0, 8)
    recentMatches.value = (matchesRes.data || []).filter(
      (m: any) => m.home_team_id === teamId || m.away_team_id === teamId
    ).slice(0, 5)
  } catch (error) {
    console.error('Failed to load team:', error)
  } finally {
    loading.value = false
  }
}

const goToPlayer = (id: string) => router.push(`/players/${id}`)
const goToMatch = (id: string) => router.push(`/matches/${id}`)

onMounted(() => {
  loadTeam()
})
</script>

<style scoped>
.team-detail-view {
  max-width: 1200px;
  margin: 0 auto;
}

.team-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.team-info {
  display: flex;
  gap: 30px;
  align-items: center;
}

.team-logo {
  font-size: 72px;
}

.team-name {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 5px;
}

.team-name-cn {
  font-size: 18px;
  color: #606266;
  margin-bottom: 10px;
}

.team-country, .team-founded {
  font-size: 14px;
  color: #909399;
}

.team-stats-summary {
  display: flex;
  gap: 40px;
}

.stat {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
  display: block;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.stats-grid {
  margin-top: 20px;
}

.players-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
}

.player-item {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: background 0.2s;
}

.player-item:hover {
  background: #e4e7ed;
}

.player-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.player-position {
  font-size: 12px;
  color: #909399;
  margin: 5px 0;
}

.player-value {
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
}

.matches-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.match-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.match-item:hover {
  background: #e4e7ed;
}

.match-teams {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.match-score {
  font-size: 16px;
  font-weight: 700;
  color: #409eff;
}

.match-time {
  font-size: 12px;
  color: #909399;
}
</style>