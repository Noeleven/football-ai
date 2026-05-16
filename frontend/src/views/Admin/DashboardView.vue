<template>
  <div class="dashboard-view">
    <h1>{{ t('admin.dashboard') }}</h1>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">⚽</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.teams }}</div>
          <div class="stat-label">Teams</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏃</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.players }}</div>
          <div class="stat-label">Players</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📅</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.matches }}</div>
          <div class="stat-label">Matches</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📰</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.news }}</div>
          <div class="stat-label">News</div>
        </div>
      </div>
    </div>

    <!-- System Status -->
    <div class="card">
      <h3 class="card-title">System Status</h3>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Database">Connected</el-descriptions-item>
        <el-descriptions-item label="Redis Cache">Active</el-descriptions-item>
        <el-descriptions-item label="LLM Service">Ready</el-descriptions-item>
        <el-descriptions-item label="Collector Service">Running</el-descriptions-item>
      </el-descriptions>
    </div>

    <!-- Recent Activity -->
    <div class="card">
      <h3 class="card-title">Recent Activity</h3>
      <el-table :data="recentActivity" style="width: 100%">
        <el-table-column prop="time" label="Time" width="180" />
        <el-table-column prop="action" label="Action" />
        <el-table-column prop="target" label="Target" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const stats = ref({
  teams: 0,
  players: 0,
  matches: 0,
  news: 0,
})

const recentActivity = ref([
  { time: '2024-01-15 10:30', action: 'Prediction Generated', target: 'Match WC2026-GA-1-2' },
  { time: '2024-01-15 09:15', action: 'News Collected', target: '15 news items' },
  { time: '2024-01-15 08:00', action: 'System Started', target: 'All services' },
])

onMounted(() => {
  // Load dashboard stats
})
</script>

<style scoped>
.dashboard-view {
  max-width: 1200px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.stat-icon {
  font-size: 36px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}
</style>