<template>
  <CrudView
    title="Matches Management"
    :columns="columns"
    :data-loader="loadMatches"
  />
</template>

<script setup lang="ts">
import CrudView from './CrudView.vue'
import { getUpcomingMatches } from '@/services/api'

const columns = [
  { prop: 'match_id', label: 'ID' },
  { prop: 'home_team_name', label: 'Home' },
  { prop: 'away_team_name', label: 'Away' },
  { prop: 'match_time', label: 'Time' },
  { prop: 'competition_name', label: 'Competition' },
  { prop: 'status', label: 'Status' },
]

const loadMatches = async () => {
  const res = await getUpcomingMatches('', 100)
  return res.data || []
}
</script>