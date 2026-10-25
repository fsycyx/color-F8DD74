<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import { AlertCircle, ArrowRight, Check, CheckCircle2, ImagePlus, LoaderCircle, Pencil, RefreshCcw, Send, ShieldCheck, Sparkles, UploadCloud, X } from 'lucide-vue-next'
import EmptyState from '../components/EmptyState.vue'
import { buildPlans, recognizeMenu } from '../services/mockApi'
import { useHealthStore } from '../stores/health'
import type { MealPlan, MenuItem } from '../types'

const health = useHealthStore()
const imageUrl = ref('')
const fileName = ref('')
const step = ref<'upload' | 'review' | 'plans'>('upload')
const loading = ref(false)
const error = ref('')
const menuItems = ref<MenuItem[]>([])
const plans = ref<MealPlan[]>([])
const request = ref('不要辣，预算 25 元，今天想多吃蔬菜')
const reviseText = ref('')
const savedId = ref('')

const averageConfidence = computed(() => {
  if (!menuItems.value.length) return 0
  const total = menuItems.value.reduce((sum, item) => sum + item.confidence, 0)
  return Math.round((total / menuItems.value.length) * 100)
})

function releasePreviewUrl() {
  if (!imageUrl.value) return
  URL.revokeObjectURL(imageUrl.value)
  imageUrl.value = ''
}

function handleFile(event: Event) {
  const files = (event.target as HTMLInputElement).files
  if (!files?.length) return

  // 上传图片只生成本地预览地址；切换图片时及时释放旧地址，避免内存泄漏。
  releasePreviewUrl()
  fileName.value = files[0].name
  imageUrl.value = URL.createObjectURL(files[0])
  error.value = ''
}

async function analyze() {
  if (!imageUrl.value) {
    error.value = '请先选择一张菜单图片或截图。'
    return
  }
  loading.value = true
  error.value = ''
  try {
    menuItems.value = await recognizeMenu()
    step.value = 'review'
  } catch {
    error.value = '暂时无法识别图片，请稍后重试或手动录入。'
  } finally { loading.value = false }
}

async function generatePlans(extra = '') {
  loading.value = true
  error.value = ''
  try {
    plans.value = await buildPlans(menuItems.value, `${request.value} ${extra}`)
    step.value = 'plans'
    reviseText.value = ''
  } catch {
    error.value = '方案生成失败，已保留识别结果，请重新尝试。'
  } finally { loading.value = false }
}

function choosePlan(plan: MealPlan) {
  // 用户主动确认后才写入今日记录，Agent 不自动执行有状态操作。
  health.savePlan(plan)
  savedId.value = plan.id
}

function reset() {
  releasePreviewUrl()
  step.value = 'upload'
  fileName.value = ''
  menuItems.value = []
  plans.value = []
  error.value = ''
  savedId.value = ''
}

onBeforeUnmount(releasePreviewUrl)
</script>

<template>
  <section class="page meal-page">
    <div class="page-intro">
      <div><span class="eyebrow">从当前可选项中做决定</span><h2>今天这顿，怎么选更合适？</h2><p>上传菜单后校正识别结果，系统会结合预算、忌口与今日记录生成可比较方案。</p></div>
      <div class="steps" aria-label="点餐步骤">
        <span :class="{ active: step === 'upload', done: step !== 'upload' }">1 上传</span><i /><span :class="{ active: step === 'review', done: step === 'plans' }">2 校正</span><i /><span :class="{ active: step === 'plans' }">3 决策</span>
      </div>
    </div>

    <div v-if="error" class="alert error"><AlertCircle :size="18" /><span>{{ error }}</span><button type="button" aria-label="关闭" @click="error = ''"><X :size="17" /></button></div>

    <!-- 上传、人工校正、方案决策组成可回退的三阶段流程。 -->
    <div v-if="step === 'upload'" class="meal-workspace two-column">
      <article class="panel upload-panel">
        <div class="panel-heading"><div><span class="section-kicker">第一步</span><h3>上传菜单或外卖截图</h3></div><UploadCloud :size="23" /></div>
        <label class="drop-zone" :class="{ hasImage: imageUrl }">
          <input type="file" accept="image/*" @change="handleFile" />
          <img v-if="imageUrl" :src="imageUrl" alt="待识别菜单预览" />
          <template v-else><ImagePlus :size="34" /><strong>选择图片</strong><span>支持 JPG、PNG，建议文字清晰且画面端正</span></template>
        </label>
        <div v-if="fileName" class="file-row"><CheckCircle2 :size="17" />{{ fileName }}<button type="button" @click="reset"><X :size="16" /></button></div>
        <button class="primary-button full" type="button" :disabled="loading" @click="analyze"><LoaderCircle v-if="loading" class="spin" :size="18" /><Sparkles v-else :size="18" />{{ loading ? '正在识别菜名与价格…' : '开始智能识别' }}</button>
        <p class="privacy-note"><ShieldCheck :size="15" />演示版仅在浏览器显示上传图片，不会发送或保存原图。</p>
      </article>
      <aside class="panel preference-panel">
        <span class="section-kicker">本餐偏好</span><h3>告诉系统你更在意什么</h3>
        <label>自然语言描述<textarea v-model="request" rows="4" placeholder="例如：预算 25 元，不要辣，想吃得饱一点" /></label>
        <div class="chip-row"><button v-for="chip in ['预算 25 元', '不要辣', '补充蔬菜', '高蛋白']" :key="chip" type="button" @click="request = `${request}，${chip}`">+ {{ chip }}</button></div>
        <div class="context-box"><strong>已读取今日状态</strong><ul><li>蔬菜约 220 g，晚餐可以补充</li><li>活动 32 分钟，属于一般活动日</li><li>未设置食物过敏信息</li></ul></div>
      </aside>
    </div>

    <!-- 低置信识别必须先由用户校正，不能直接进入营养计算。 -->
    <div v-else-if="step === 'review'" class="review-layout">
      <article class="panel image-review"><img :src="imageUrl" alt="上传的菜单" /><button class="secondary-button" type="button" @click="step = 'upload'"><RefreshCcw :size="16" />更换图片</button></article>
      <article class="panel review-table-card">
        <div class="panel-heading"><div><span class="section-kicker">识别校正</span><h3>请确认菜名与价格</h3></div><span class="confidence">平均置信度 {{ averageConfidence }}%</span></div>
        <p>橙色行置信度较低。错误数据会直接影响方案，请先修改再继续。</p>
        <div class="menu-table" role="table">
          <div class="table-row table-head" role="row"><span>菜品</span><span>价格</span><span>置信度</span><span></span></div>
          <div v-for="item in menuItems" :key="item.id" class="table-row" :class="{ uncertain: item.confidence < .8 }" role="row">
            <input v-model="item.name" :aria-label="`${item.name}菜名`" /><label><span>¥</span><input v-model.number="item.price" type="number" :aria-label="`${item.name}价格`" /></label><span class="confidence-bar"><i :style="{ width: `${item.confidence * 100}%` }" />{{ Math.round(item.confidence * 100) }}%</span><Pencil :size="15" />
          </div>
        </div>
        <button class="primary-button full" type="button" :disabled="loading" @click="generatePlans()"><LoaderCircle v-if="loading" class="spin" :size="18" /><ArrowRight v-else :size="18" />{{ loading ? '正在计算约束与组合…' : '确认并生成方案' }}</button>
      </article>
    </div>

    <!-- 最终方案展示范围估算和推荐理由，不宣称精确营养结果。 -->
    <template v-else>
      <div class="recommendation-summary"><div><span class="eyebrow">基于 5 个已确认菜品</span><h3>三个方案，各有清楚的取舍</h3></div><button class="secondary-button" type="button" @click="step = 'review'"><Pencil :size="16" />修改菜单</button></div>
      <div v-if="loading" class="loading-block"><LoaderCircle class="spin" /><strong>正在重新检查预算与营养结构</strong><span>只重算受修改影响的方案</span></div>
      <div v-else-if="plans.length" class="plan-grid">
        <article v-for="plan in plans" :key="plan.id" class="plan-card" :class="{ selected: savedId === plan.id }" :style="{ '--accent': plan.accent }">
          <div class="plan-top"><span class="plan-tag">{{ plan.tag }}</span><strong>{{ plan.match }}<small>% 匹配</small></strong></div>
          <h3>{{ plan.title }}</h3><p>{{ plan.description }}</p>
          <ul class="food-list"><li v-for="item in plan.items" :key="item"><Check :size="15" />{{ item }}</li></ul>
          <div class="nutrition-grid"><div><span>价格</span><strong>¥{{ plan.price }}</strong></div><div><span>能量估算</span><strong>{{ plan.calories[0] }}–{{ plan.calories[1] }} kcal</strong></div><div><span>蛋白质</span><strong>约 {{ plan.protein }} g</strong></div><div><span>蔬菜</span><strong>约 {{ plan.vegetable }} g</strong></div></div>
          <div class="reason-box"><strong>为什么这样推荐</strong><span v-for="reason in plan.reasons" :key="reason">· {{ reason }}</span></div>
          <button class="plan-button" type="button" @click="choosePlan(plan)"><CheckCircle2 :size="17" />{{ savedId === plan.id ? '已加入今日记录' : '选择此方案' }}</button>
        </article>
      </div>
      <EmptyState v-else title="暂无可用方案" detail="返回校正菜单，确认至少保留一个可选菜品。" />
      <article class="panel revise-panel">
        <div><span class="section-kicker">继续调整</span><h3>一句话换菜，查看变化</h3><p>例如：“不要牛肉，再便宜 5 元”或“蔬菜多一点”。</p></div>
        <div class="revise-input"><input v-model="reviseText" placeholder="输入你的修改要求" @keyup.enter="reviseText && generatePlans(reviseText)" /><button class="primary-button" type="button" :disabled="!reviseText" @click="generatePlans(reviseText)"><Send :size="17" />重新计算</button></div>
      </article>
      <p class="estimate-disclaimer">营养数据来自标准食物成分估算，以范围展示；实际数值会因食材、份量和烹饪方式变化。</p>
    </template>
  </section>
</template>
