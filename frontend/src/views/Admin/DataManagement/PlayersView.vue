<template>
  <CrudView
    title="Players Management"
    :columns="columns"
    :data-loader="loadPlayers"
  />
</template>

<script setup lang="ts">
import CrudView from './CrudView.vue'
import { searchPlayers } from '@/services/api'

const columns = [
  { prop: 'player_id', label: 'ID' },
  { prop: 'name', label: 'Name' },
  { prop: 'position', label: 'Position' },
  { prop: 'nationality', label: 'Nationality' },
  { prop: 'team_name', label: 'Team' },
  { prop: 'market_value', label: 'Value (M)' },
]

const loadPlayers = async () => {
  const res = await searchPlayers('')
  return res.data || []
}
</script>