<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart, LineChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { ArrowDownRight, ArrowUpRight, CalendarDays, CheckCircle2, Lightbulb, Moon, MoveRight, Target } from 'lucide-vue-next'
import { useHealthStore } from '../stores/health'

echarts.use([LineChart, BarChart, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer])

const health = useHealthStore()
const metric = ref<'water' | 'sleep' | 'activity'>('water')
const chartEl = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

// 所有指标共用同一张图表，通过配置映射切换数据、单位和主题色。
const configs = computed(() => ({
  water: { name: '饮水', unit: 'ml', color: '#2878a6', data: health.week.map((d) => d.water) },
  sleep: { name: '睡眠', unit: '小时', color: '#6755a6', data: health.week.map((d) => d.sleep) },
  activity: { name: '活动', unit: '分钟', color: '#287b55', data: health.week.map((d) => d.activity) },
})[metric.value])

function renderChart() {
  if (!chartEl.value) return

  // 图表实例只初始化一次，切换指标时通过 setOption 更新，避免重复占用 Canvas 资源。
  chart ??= echarts.init(chartEl.value)
  const cfg = configs.value
  chart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (v: unknown) => `${v} ${cfg.unit}` },
    grid: { left: 16, right: 14, top: 28, bottom: 18, containLabel: true },
    xAxis: { type: 'category', data: health.week.map((d) => d.day), axisLine: { lineStyle: { color: '#d9dfd8' } }, axisTick: { show: false } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#edf0ec' } }, axisLabel: { color: '#7b827d' } },
    series: [{ name: cfg.name, type: metric.value === 'activity' ? 'bar' : 'line', smooth: true, symbolSize: 8, data: cfg.data, itemStyle: { color: cfg.color }, lineStyle: { width: 3, color: cfg.color }, areaStyle: metric.value !== 'activity' ? { color: `${cfg.color}18` } : undefined, barWidth: 24 }],
  })
}

const resize = () => chart?.resize()
onMounted(() => {
  nextTick(renderChart)
  window.addEventListener('resize', resize)
})

watch(metric, () => nextTick(renderChart))

onBeforeUnmount(() => {
  // 离开页面时解除全局监听并销毁实例，防止路由反复进入后产生泄漏。
  window.removeEventListener('resize', resize)
  chart?.dispose()
})
</script>

<template>
  <section class="page insights-page">
    <div class="page-intro"><div><span class="eyebrow">过去 7 天 · 记录完整度 86%</span><h2>趋势比单日数字更有意义。</h2><p>以下结论只基于你主动记录的数据，用来帮助复盘习惯，不用于判断疾病或健康风险。</p></div><button class="secondary-button"><CalendarDays :size="17" />10 月 12 日–18 日</button></div>
    <div class="insight-summary-grid">
      <article><span>平均睡眠</span><strong>7.0<small> 小时</small></strong><p class="positive"><ArrowUpRight :size="15" />较上周 +0.4 小时</p></article>
      <article><span>平均饮水</span><strong>1643<small> ml</small></strong><p class="positive"><ArrowUpRight :size="15" />较上周 +180 ml</p></article>
      <article><span>平均活动</span><strong>36<small> 分钟</small></strong><p class="negative"><ArrowDownRight :size="15" />较上周 -6 分钟</p></article>
      <article><span>蔬菜达标日</span><strong>3<small> / 7 天</small></strong><p class="neutral"><MoveRight :size="15" />与上周持平</p></article>
    </div>
    <!-- 洞察只描述记录中的关联，不将相关性表述为医学因果。 -->
    <div class="insights-layout">
      <article class="panel chart-panel">
        <div class="panel-heading"><div><span class="section-kicker">七日变化</span><h3>{{ configs.name }}趋势</h3></div><div class="chart-tabs"><button v-for="item in [{id:'water',label:'饮水'},{id:'sleep',label:'睡眠'},{id:'activity',label:'活动'}]" :key="item.id" :class="{ active: metric === item.id }" @click="metric = item.id as typeof metric">{{ item.label }}</button></div></div>
        <div ref="chartEl" class="health-chart" aria-label="七日健康趋势图" />
      </article>
      <article class="panel pattern-panel">
        <div class="panel-heading"><div><span class="section-kicker">记录中的关联</span><h3>这周观察到什么</h3></div><Lightbulb /></div>
        <div class="pattern-item"><span class="pattern-icon"><Moon /></span><div><strong>睡眠较短的两天，含糖饮品记录更多</strong><p>周一、周五睡眠不足 6.5 小时，同日各有 2 次含糖饮品记录。这只是数据关联，不代表因果。</p></div></div>
        <div class="pattern-item"><span class="pattern-icon green"><CheckCircle2 /></span><div><strong>午餐有蔬菜时，晚间加餐更少</strong><p>有 4 天午餐记录了蔬菜，其中 3 天没有晚间加餐。</p></div></div>
      </article>
      <article class="panel goal-panel">
        <div class="panel-heading"><div><span class="section-kicker">下周小行动</span><h3>只选三个能做到的改变</h3></div><Target /></div>
        <ol><li><span>1</span><div><strong>上午固定补水一次</strong><p>把 350 ml 饮水安排在第一节课后。</p></div><button type="button">采用</button></li><li><span>2</span><div><strong>午餐优先确认蔬菜</strong><p>点主菜前先从菜单中选一份蔬菜。</p></div><button type="button">采用</button></li><li><span>3</span><div><strong>工作日增加 10 分钟步行</strong><p>选三个最容易安排的晚上执行。</p></div><button type="button">采用</button></li></ol>
      </article>
    </div>
  </section>
</template>
