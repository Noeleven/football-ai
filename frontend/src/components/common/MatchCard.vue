<template>
  <div class="match-card" @click="goToMatch">
    <div class="match-time">{{ formatTime(match.match_time) }}</div>
    <div class="match-teams">
      <div class="team home">
        <div class="team-logo">{{ getTeamEmoji(match.home_team_name) }}</div>
        <div class="team-name">{{ match.home_team_name }}</div>
      </div>
      <div class="vs">
        <span v-if="match.status === 'finished'">{{ match.home_score }} - {{ match.away_score }}</span>
        <span v-else>VS</span>
      </div>
      <div class="team away">
        <div class="team-logo">{{ getTeamEmoji(match.away_team_name) }}</div>
        <div class="team-name">{{ match.away_team_name }}</div>
      </div>
    </div>
    <div class="match-info">
      <span class="competition">{{ match.competition_name }}</span>
      <span class="round">{{ match.round }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'

const props = defineProps<{
  match: {
    match_id: string
    home_team_name: string
    away_team_name: string
    home_score?: number
    away_score?: number
    match_time: string
    competition_name: string
    round: string
    status: string
  }
}>()

const router = useRouter()

const formatTime = (time: string) => {
  return dayjs(time).format('MM/DD HH:mm')
}

const getTeamEmoji = (name: string) => {
  const emojis: Record<string, string> = {
    'Argentina': '🇦🇷', 'Brazil': '🇧🇷', 'France': '🇫🇷', 'Germany': '🇩🇪',
    'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Spain': '🇪🇸', 'Italy': '🇮🇹',
  }
  return emojis[name] || '⚽'
}

const goToMatch = () => {
  router.push(`/matches/${props.match.match_id}`)
}
</script>

<style scoped>
.match-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.match-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.match-time {
  text-align: center;
  color: #909399;
  font-size: 14px;
  margin-bottom: 15px;
}

.match-teams {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
}

.team {
  text-align: center;
  flex: 1;
}

.team-logo {
  font-size: 32px;
  margin-bottom: 8px;
}

.team-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.vs {
  font-size: 18px;
  font-weight: 700;
  color: #409eff;
  padding: 0 10px;
}

.match-info {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.competition, .round {
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}
</style>