<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'
import { AlertTriangle, Bell, Check, Database, Download, Eye, LockKeyhole, ShieldCheck, Trash2, UserRound } from 'lucide-vue-next'
import { useHealthStore } from '../stores/health'

const health = useHealthStore()
const name = ref('林同学')
const budget = ref(25)
const avoid = ref('不吃香菜，不喜欢太辣')
const saved = ref(false)
const showConfirm = ref(false)
let saveFeedbackTimer: number | undefined

function save() {
  saved.value = true
  window.clearTimeout(saveFeedbackTimer)
  saveFeedbackTimer = window.setTimeout(() => {
    saved.value = false
  }, 1600)
}

function clearData() {
  // 删除动作必须由二次确认触发；Store 负责清理持久化数据并恢复空状态。
  health.clearLocalData()
  showConfirm.value = false
}

onBeforeUnmount(() => window.clearTimeout(saveFeedbackTimer))
</script>

<template>
  <section class="page settings-page">
    <div class="page-intro"><div><span class="eyebrow">个人资料与数据控制</span><h2>设置与隐私</h2><p>你可以随时修改偏好、关闭提醒、导出或删除本地记录。</p></div></div>
    <!-- 偏好、隐私和健康边界分区展示，敏感操作使用二次确认。 -->
    <div class="settings-layout">
      <nav class="settings-nav"><a href="#profile" class="active"><UserRound />个人偏好</a><a href="#privacy"><LockKeyhole />隐私与数据</a><a href="#boundary"><ShieldCheck />健康边界</a></nav>
      <div class="settings-content">
        <article id="profile" class="panel settings-section"><div class="settings-title"><UserRound /><div><h3>个人偏好</h3><p>这些信息用于筛选点餐方案，不代表医学档案。</p></div></div><div class="form-grid"><label>显示名称<input v-model="name" /></label><label>单餐常用预算<input v-model.number="budget" type="number" /><span class="input-suffix">元</span></label><label class="full-field">饮食偏好与忌口<textarea v-model="avoid" rows="3" /></label><fieldset class="full-field"><legend>已知食物过敏</legend><div class="check-grid"><label v-for="item in ['花生','坚果','乳制品','蛋','大豆','甲壳类']" :key="item"><input type="checkbox" />{{ item }}</label></div><small>严重过敏者仍需查看实物配料并向商家确认交叉污染风险。</small></fieldset></div><button class="primary-button" type="button" @click="save"><Check :size="17" />{{ saved ? '已保存' : '保存偏好' }}</button></article>
        <article id="privacy" class="panel settings-section"><div class="settings-title"><LockKeyhole /><div><h3>隐私与数据</h3><p>演示版记录仅保存在当前浏览器。</p></div></div><div class="setting-row"><span class="setting-icon"><Bell /></span><div><strong>健康行动提醒</strong><p>在你设定的时间显示饮水、久坐与记录提醒。</p></div><label class="switch"><input v-model="health.notifications" type="checkbox" /><i /></label></div><div class="setting-row"><span class="setting-icon"><Eye /></span><div><strong>改进匿名体验数据</strong><p>默认关闭，不上传健康记录或图片。</p></div><label class="switch"><input type="checkbox" /><i /></label></div><div class="data-actions"><button class="secondary-button" type="button"><Download />导出我的数据</button><button class="danger-button" type="button" @click="showConfirm = true"><Trash2 />删除本地数据</button></div></article>
        <article id="boundary" class="panel settings-section boundary-section"><div class="settings-title"><ShieldCheck /><div><h3>健康边界</h3><p>餐衡适用于普通成年人的日常健康信息管理。</p></div></div><div class="boundary-grid"><div><strong>可以做</strong><ul><li>整理一般膳食与生活方式资料</li><li>估算食物营养范围</li><li>记录并总结用户主动输入的数据</li><li>发现约束冲突和潜在过敏原</li></ul></div><div><strong>不会做</strong><ul><li>诊断、治疗或预测疾病</li><li>制定疾病饮食和用药方案</li><li>承诺精准减重或营养结果</li><li>替代医生或注册营养师</li></ul></div></div><div class="medical-notice"><AlertTriangle /><p>涉及疾病、孕产期、未成年人、进食障碍或急性不适时，系统会停止个性化建议并建议咨询专业人员。如有紧急症状，请立即联系当地急救服务。</p></div></article>
      </div>
    </div>
    <div v-if="showConfirm" class="modal-backdrop" @click.self="showConfirm = false"><div class="confirm-dialog"><span class="danger-icon"><Trash2 /></span><h3>删除全部本地记录？</h3><p>这会清除今日记录、已选餐食和偏好数据。此操作无法撤销。</p><div><button class="secondary-button" @click="showConfirm = false">取消</button><button class="danger-button" @click="clearData">确认删除</button></div></div></div>
  </section>
</template>
