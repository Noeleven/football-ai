<template>
  <div class="win-rate-pie">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  data: Array<{ name: string; value: number }>
  title?: string
}>()

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)
  const option = {
    title: {
      text: props.title || 'Win Rate',
      left: 'center',
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}% ({d}%)',
    },
    legend: {
      bottom: 0,
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      label: {
        show: true,
        formatter: '{b}: {c}%',
      },
      data: props.data.map(item => ({
        ...item,
        value: Math.round(item.value * 100),
      })),
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
.win-rate-pie {
  width: 100%;
}

.chart-container {
  width: 100%;
  height: 300px;
}
</style>