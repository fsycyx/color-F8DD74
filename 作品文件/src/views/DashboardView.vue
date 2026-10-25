<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { Activity, ArrowRight, Check, Droplets, Moon, Plus, Salad, Sparkles, Utensils } from 'lucide-vue-next'
import MetricCard from '../components/MetricCard.vue'
import { useHealthStore } from '../stores/health'

const health = useHealthStore()

// 问候语只根据本地时间展示，不参与任何健康判断。
const greeting = computed(() => {
  const currentHour = new Date().getHours()
  if (currentHour < 12) return '早上好'
  if (currentHour < 18) return '下午好'
  return '晚上好'
})
</script>

<template>
  <section class="page dashboard-page">
    <!-- 首屏优先呈现一个可执行动作，避免把首页做成只有数字的仪表盘。 -->
    <div class="welcome-row">
      <div><p class="eyebrow">{{ greeting }}，林同学</p><h2>先照顾好今天，再慢慢变得更好。</h2><p>根据你的记录，今天最值得做的是补一份蔬菜，并在下午安排一次短时活动。</p></div>
      <RouterLink to="/meal" class="primary-button"><Utensils :size="18" />开始智能点餐</RouterLink>
    </div>

    <div class="metric-grid">
      <MetricCard label="饮水" :value="`${health.today.water} ml`" hint="参考目标 1800 ml" :progress="health.waterPercent" :icon="Droplets" tone="#2878a6" />
      <MetricCard label="睡眠" :value="`${health.today.sleep} 小时`" hint="昨晚 · 主观质量良好" :progress="Math.round(health.today.sleep / 8 * 100)" :icon="Moon" tone="#6755a6" />
      <MetricCard label="活动" :value="`${health.today.activity} 分钟`" hint="参考目标 45 分钟" :progress="health.activityPercent" :icon="Activity" tone="#287b55" />
      <MetricCard label="蔬菜" value="220 g" hint="晚餐建议再补一份" :progress="55" :icon="Salad" tone="#b1642d" />
    </div>

    <!-- 快捷操作、时间线和点餐计划共享 Pinia 中的今日状态。 -->
    <div class="dashboard-grid">
      <article class="panel next-action">
        <div class="panel-heading"><div><span class="section-kicker">下一步行动</span><h3>16:30 前，离开座位活动 10 分钟</h3></div><span class="status-pill"><Sparkles :size="14" />AI 建议</span></div>
        <p>你已连续坐了约 96 分钟。一次轻量步行比追求高强度训练更容易在今天完成。</p>
        <div class="action-buttons"><button class="primary-button" type="button"><Check :size="17" />标记完成</button><button class="secondary-button" type="button">稍后提醒</button></div>
      </article>

      <article class="panel water-panel">
        <div class="panel-heading"><div><span class="section-kicker">快速记录</span><h3>补充饮水</h3></div><Droplets :size="22" /></div>
        <div class="water-actions">
          <button v-for="amount in [200, 350, 500]" :key="amount" type="button" @click="health.addWater(amount)"><Plus :size="16" />{{ amount }} ml</button>
        </div>
        <small>饮水建议是一般参考，天气和活动量会影响实际需要。</small>
      </article>

      <article class="panel today-log">
        <div class="panel-heading"><div><span class="section-kicker">今日记录</span><h3>你的健康时间线</h3></div><RouterLink to="/records" class="text-link">全部记录 <ArrowRight :size="15" /></RouterLink></div>
        <ol class="timeline">
          <li><span class="time">08:10</span><span class="timeline-dot green" /><div><strong>早餐已记录</strong><p>燕麦、鸡蛋、苹果 · 结构完整</p></div></li>
          <li><span class="time">11:40</span><span class="timeline-dot blue" /><div><strong>饮水 350 ml</strong><p>今日累计 {{ health.today.water }} ml</p></div></li>
          <li><span class="time">13:05</span><span class="timeline-dot orange" /><div><strong>午餐已记录</strong><p>米饭、清蒸鸡腿、番茄炒蛋</p></div></li>
          <li class="future"><span class="time">16:30</span><span class="timeline-dot" /><div><strong>活动提醒</strong><p>建议步行或拉伸 10 分钟</p></div></li>
        </ol>
      </article>

      <article class="panel meal-card">
        <div class="meal-photo" role="img" aria-label="一份包含谷物、鸡肉和蔬菜的均衡餐食" />
        <div class="meal-copy"><span class="section-kicker">今天的饮食</span><h3>{{ health.selectedPlan ? health.selectedPlan.title : '晚餐还没有计划' }}</h3><p>{{ health.selectedPlan ? health.selectedPlan.items.join(' · ') : '上传食堂菜单，看看当前真正能买到的更合适选择。' }}</p><RouterLink to="/meal" class="text-link">{{ health.selectedPlan ? '查看方案' : '规划晚餐' }} <ArrowRight :size="15" /></RouterLink></div>
      </article>
    </div>
  </section>
</template>
