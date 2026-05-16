<template>
  <div class="teams-view page-container">
    <h1 class="page-title">{{ t('teams.title') }}</h1>

    <!-- Search -->
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        :placeholder="t('teams.search_placeholder')"
        @change="searchTeams"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- Teams Grid -->
    <div class="teams-grid" v-loading="loading">
      <div
        v-for="team in teams"
        :key="team.team_id"
        class="team-card"
        @click="goToTeam(team.team_id)"
      >
        <div class="team-logo">{{ getTeamEmoji(team.name) }}</div>
        <div class="team-name">{{ team.name }}</div>
        <div class="team-name-cn">{{ team.name_cn }}</div>
        <div class="team-country">{{ team.country }}</div>
      </div>
      <div v-if="!loading && teams.length === 0" class="no-data">
        No teams found
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Search } from '@element-plus/icons-vue'
import { getTeams, searchTeams as apiSearchTeams } from '@/services/api'

const { t } = useI18n()
const router = useRouter()

const teams = ref<any[]>([])
const loading = ref(false)
const searchKeyword = ref('')

const getTeamEmoji = (name: string) => {
  const emojis: Record<string, string> = {
    'Argentina': '🇦🇷', 'Brazil': '🇧🇷', 'France': '🇫🇷', 'Germany': '🇩🇪',
    'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Spain': '🇪🇸', 'Italy': '🇮🇹',
  }
  return emojis[name] || '⚽'
}

const loadTeams = async () => {
  loading.value = true
  try {
    const res = await getTeams()
    teams.value = res.data || []
  } catch (error) {
    console.error('Failed to load teams:', error)
  } finally {
    loading.value = false
  }
}

const searchTeams = async () => {
  if (!searchKeyword.value.trim()) {
    loadTeams()
    return
  }
  loading.value = true
  try {
    const res = await apiSearchTeams(searchKeyword.value)
    teams.value = res.data || []
  } catch (error) {
    console.error('Failed to search teams:', error)
  } finally {
    loading.value = false
  }
}

const goToTeam = (id: string) => {
  router.push(`/teams/${id}`)
}

onMounted(() => {
  loadTeams()
})
</script>

<style scoped>
.teams-view {
  max-width: 1200px;
  margin: 0 auto;
}

.search-bar {
  margin-bottom: 30px;
  max-width: 400px;
}

.teams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.team-card {
  background: #fff;
  border-radius: 12px;
  padding: 30px 20px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.team-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.team-logo {
  font-size: 48px;
  margin-bottom: 15px;
}

.team-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
}

.team-name-cn {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.team-country {
  font-size: 12px;
  color: #909399;
}

.no-data {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px;
  color: #909399;
}
</style>