<template>
  <div class="stats-chart">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  data: {
    labels: string[]
    values: number[]
    title?: string
    color?: string
  }
  type?: 'bar' | 'line' | 'pie'
}>()

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)
  const option = {
    title: {
      text: props.data.title || '',
      left: 'center',
    },
    tooltip: {},
    xAxis: {
      type: 'category',
      data: props.data.labels,
    },
    yAxis: {
      type: 'value',
    },
    series: [{
      type: props.type || 'bar',
      data: props.data.values,
      itemStyle: {
        color: props.data.color || '#409eff',
      },
    }],
  }
  chart.setOption(option)
}

onMounted(() => {
  initChart()
})

watch(() => props.data, () => {
  initChart()
}, { deep: true })

onUnmounted(() => {
  chart?.dispose()
})
</script>

<style scoped>
.stats-chart {
  width: 100%;
}

.chart-container {
  width: 100%;
  height: 300px;
}
</style>