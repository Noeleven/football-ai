<template>
  <CrudView
    title="Teams Management"
    :columns="columns"
    :data-loader="loadTeams"
  />
</template>

<script setup lang="ts">
import CrudView from './CrudView.vue'
import { getTeams } from '@/services/api'

const columns = [
  { prop: 'team_id', label: 'ID' },
  { prop: 'name', label: 'Name' },
  { prop: 'name_cn', label: 'Chinese Name' },
  { prop: 'country', label: 'Country' },
  { prop: 'stadium', label: 'Stadium' },
  { prop: 'style', label: 'Style' },
]

const loadTeams = async () => {
  const res = await getTeams()
  return res.data || []
}
</script>