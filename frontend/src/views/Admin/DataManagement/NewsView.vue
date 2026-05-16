<template>
  <CrudView
    title="News Management"
    :columns="columns"
    :data-loader="loadNews"
  />
</template>

<script setup lang="ts">
import CrudView from './CrudView.vue'
import { getRecentNews } from '@/services/api'

const columns = [
  { prop: 'news_id', label: 'ID' },
  { prop: 'title', label: 'Title' },
  { prop: 'news_type', label: 'Type' },
  { prop: 'source', label: 'Source' },
  { prop: 'published_at', label: 'Published' },
  { prop: 'view_count', label: 'Views' },
]

const loadNews = async () => {
  const res = await getRecentNews(100)
  return res.data || []
}
</script>