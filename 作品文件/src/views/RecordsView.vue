<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'
import { Activity, AlertTriangle, Camera, CheckCircle2, ChevronRight, Coffee, Droplets, FileText, Heart, LoaderCircle, Moon, Plus, ScanLine, Smile, TimerReset } from 'lucide-vue-next'
import { useHealthStore } from '../stores/health'

const health = useHealthStore()
const activeTab = ref<'daily' | 'label'>('daily')
const saved = ref('')
const labelImage = ref('')
const scanning = ref(false)
const scanComplete = ref(false)
const moodOptions = ['轻松', '平稳', '疲惫', '压力较大']
let saveFeedbackTimer: number | undefined
let scanTimer: number | undefined

function save(kind: string) {
  saved.value = kind
  window.clearTimeout(saveFeedbackTimer)
  saveFeedbackTimer = window.setTimeout(() => {
    saved.value = ''
  }, 1800)
}

function releaseLabelPreview() {
  if (!labelImage.value) return
  URL.revokeObjectURL(labelImage.value)
  labelImage.value = ''
}

function handleLabel(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  // 标签图片当前仅用于本地预览，正式接入上传接口后仍应遵循最短保存原则。
  releaseLabelPreview()
  labelImage.value = URL.createObjectURL(file)
  scanComplete.value = false
}

function scanLabel() {
  if (!labelImage.value) return
  scanning.value = true
  window.clearTimeout(scanTimer)
  scanTimer = window.setTimeout(() => {
    scanning.value = false
    scanComplete.value = true
  }, 1100)
}

onBeforeUnmount(() => {
  releaseLabelPreview()
  window.clearTimeout(saveFeedbackTimer)
  window.clearTimeout(scanTimer)
})
</script>

<template>
  <section class="page records-page">
    <div class="page-intro"><div><span class="eyebrow">十秒完成一条记录</span><h2>记录事实，不评判每一次选择。</h2><p>数据越完整，系统越能给出贴近今天情境的建议；未记录的日期不会被推断。</p></div></div>
    <div class="segmented-control"><button :class="{ active: activeTab === 'daily' }" type="button" @click="activeTab = 'daily'">日常记录</button><button :class="{ active: activeTab === 'label' }" type="button" @click="activeTab = 'label'">食品标签识别</button></div>

    <!-- 日常记录全部写入同一个今日上下文，供点餐与趋势页复用。 -->
    <div v-if="activeTab === 'daily'" class="record-grid">
      <article class="panel record-card water-record">
        <div class="record-icon blue"><Droplets /></div><div class="record-heading"><span>今日饮水</span><strong>{{ health.today.water }} ml</strong></div>
        <div class="water-actions"><button v-for="amount in [200, 350, 500]" :key="amount" type="button" @click="health.addWater(amount)"><Plus :size="16" />{{ amount }}</button></div>
        <div class="record-progress"><span :style="{ width: `${health.waterPercent}%` }" /></div><small>参考目标 1800 ml · 当前 {{ health.waterPercent }}%</small>
      </article>

      <article class="panel record-card">
        <div class="record-icon purple"><Moon /></div><div class="record-heading"><span>昨晚睡眠</span><strong>{{ health.today.sleep }} 小时</strong></div>
        <label>睡眠时长 <input v-model.number="health.today.sleep" type="range" min="3" max="12" step="0.1" /><b>{{ health.today.sleep }}h</b></label>
        <label>主观质量 <select><option>很好</option><option selected>良好</option><option>一般</option><option>较差</option></select></label>
        <button class="secondary-button full" type="button" @click="save('sleep')"><CheckCircle2 :size="16" />{{ saved === 'sleep' ? '已保存' : '保存睡眠记录' }}</button>
      </article>

      <article class="panel record-card">
        <div class="record-icon green"><Activity /></div><div class="record-heading"><span>活动与久坐</span><strong>{{ health.today.activity }} 分钟</strong></div>
        <label>活动分钟 <input v-model.number="health.today.activity" type="number" min="0" max="300" /></label>
        <div class="mini-actions"><button type="button" @click="health.today.activity += 5"><TimerReset :size="16" />拉伸 +5</button><button type="button" @click="health.today.activity += 10"><Activity :size="16" />步行 +10</button></div>
        <button class="secondary-button full" type="button" @click="save('activity')"><CheckCircle2 :size="16" />{{ saved === 'activity' ? '已保存' : '保存活动记录' }}</button>
      </article>

      <article class="panel record-card mood-record">
        <div class="record-icon orange"><Smile /></div><div class="record-heading"><span>状态与饥饿</span><strong>{{ health.today.mood }}</strong></div>
        <div class="mood-options"><button v-for="mood in moodOptions" :key="mood" :class="{ selected: health.today.mood === mood }" type="button" @click="health.today.mood = mood">{{ mood }}</button></div>
        <label>当前饥饿感 <input v-model.number="health.today.hunger" type="range" min="1" max="5" /><b>{{ health.today.hunger }}/5</b></label>
        <button class="secondary-button full" type="button" @click="save('mood')"><CheckCircle2 :size="16" />{{ saved === 'mood' ? '已保存' : '保存状态记录' }}</button>
      </article>

      <article class="panel recent-records">
        <div class="panel-heading"><div><span class="section-kicker">最近记录</span><h3>今天</h3></div></div>
        <ul class="record-list"><li><span class="record-icon small green"><FileText /></span><div><strong>午餐</strong><span>米饭、鸡腿、番茄炒蛋</span></div><time>13:05</time><ChevronRight /></li><li><span class="record-icon small blue"><Droplets /></span><div><strong>饮水</strong><span>350 ml</span></div><time>11:40</time><ChevronRight /></li><li><span class="record-icon small purple"><Moon /></span><div><strong>睡眠</strong><span>7.1 小时 · 质量良好</span></div><time>08:02</time><ChevronRight /></li></ul>
      </article>
    </div>

    <!-- 标签识别结果需要用户核对单位和份数后才能保存。 -->
    <div v-else class="label-layout">
      <article class="panel upload-panel">
        <div class="panel-heading"><div><span class="section-kicker">包装食品</span><h3>扫描营养标签与配料表</h3></div><ScanLine /></div>
        <label class="drop-zone compact" :class="{ hasImage: labelImage }"><input type="file" accept="image/*" @change="handleLabel" /><img v-if="labelImage" :src="labelImage" alt="营养标签预览" /><template v-else><Camera :size="32" /><strong>上传标签照片</strong><span>请同时拍到营养成分表和配料表</span></template></label>
        <button class="primary-button full" :disabled="!labelImage || scanning" type="button" @click="scanLabel"><LoaderCircle v-if="scanning" class="spin" /><ScanLine v-else />{{ scanning ? '正在识别单位与份数…' : '开始识别' }}</button>
      </article>
      <article v-if="scanComplete" class="panel label-result">
        <div class="panel-heading"><div><span class="section-kicker">识别结果 · 演示数据</span><h3>全麦坚果麦片</h3></div><span class="confidence">置信度 93%</span></div>
        <div class="serving-control"><span>每份 40 g</span><label>食用份数 <input type="number" value="1" min="0.5" step="0.5" /></label></div>
        <div class="nutrition-table"><div><span>能量</span><strong>672 kJ</strong></div><div><span>蛋白质</span><strong>5.2 g</strong></div><div><span>脂肪</span><strong>4.8 g</strong></div><div><span>碳水化合物</span><strong>25.6 g</strong></div><div><span>钠</span><strong>86 mg</strong></div></div>
        <div class="allergen-warning"><AlertTriangle :size="20" /><div><strong>可能含有：花生、坚果、乳制品</strong><p>配料和生产线可能调整，存在交叉污染风险。严重过敏者请以实物包装并向生产商确认。</p></div></div>
        <button class="primary-button full" type="button"><CheckCircle2 />确认并记入今天</button>
      </article>
      <article v-else class="panel scan-help"><div><Coffee :size="30" /><h3>识别前需要你确认两件事</h3><p>标签上的数据可能按“每 100 克”或“每份”标示；拍摄后仍需核对单位和实际食用份数。</p><span><Heart :size="16" />这项功能只做信息整理，不判断食品“好”或“坏”。</span></div></article>
    </div>
  </section>
</template>
