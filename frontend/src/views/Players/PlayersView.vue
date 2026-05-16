<template>
  <div class="players-view page-container" v-loading="loading">
    <h1 class="page-title">{{ t('players.title') }}</h1>

    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="Search players..."
        @change="searchPlayers"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <div class="players-grid">
      <div
        v-for="player in players"
        :key="player.player_id"
        class="player-card"
        @click="goToPlayer(player.player_id)"
      >
        <div class="player-avatar">{{ getPositionEmoji(player.position) }}</div>
        <div class="player-name">{{ player.name }}</div>
        <div class="player-name-cn">{{ player.name_cn }}</div>
        <div class="player-meta">
          <span>{{ player.position }}</span>
          <span>{{ player.nationality }}</span>
        </div>
        <div class="player-value">{{ player.market_value }}M</div>
      </div>
    </div>

    <div v-if="!loading && players.length === 0" class="no-data">
      No players found
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Search } from '@element-plus/icons-vue'
import { searchPlayers as apiSearchPlayers } from '@/services/api'

const { t } = useI18n()
const router = useRouter()

const players = ref<any[]>([])
const loading = ref(false)
const searchKeyword = ref('')

const getPositionEmoji = (position: string) => {
  const emojis: Record<string, string> = { GK: '🧤', DF: '🛡️', MF: '⚙️', FW: '⚽' }
  return emojis[position] || '⚽'
}

const searchPlayers = async () => {
  if (!searchKeyword.value.trim()) {
    return
  }
  loading.value = true
  try {
    const res = await apiSearchPlayers(searchKeyword.value)
    players.value = res.data || []
  } catch (error) {
    console.error('Failed to search players:', error)
  } finally {
    loading.value = false
  }
}

const goToPlayer = (id: string) => {
  router.push(`/players/${id}`)
}

onMounted(() => {
  // Load all players initially if needed
})
</script>

<style scoped>
.players-view {
  max-width: 1200px;
  margin: 0 auto;
}

.search-bar {
  margin-bottom: 30px;
  max-width: 400px;
}

.players-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.player-card {
  background: #fff;
  border-radius: 12px;
  padding: 25px 20px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.player-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.player-avatar {
  font-size: 40px;
  margin-bottom: 15px;
}

.player-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.player-name-cn {
  font-size: 14px;
  color: #606266;
  margin: 5px 0;
}

.player-meta {
  display: flex;
  justify-content: center;
  gap: 10px;
  font-size: 12px;
  color: #909399;
  margin: 10px 0;
}

.player-value {
  font-size: 18px;
  font-weight: 700;
  color: #409eff;
}

.no-data {
  text-align: center;
  padding: 60px;
  color: #909399;
}
</style>