<script setup lang="ts">
import type { Component } from 'vue'

/** 驾驶舱统一指标卡，progress 会在模板中限制为最多 100%。 */
defineProps<{
  label: string
  value: string
  hint: string
  progress: number
  icon: Component
  tone?: string
}>()
</script>

<template>
  <article class="metric-card">
    <div class="metric-head"><span class="metric-icon" :style="{ color: tone }"><component :is="icon" :size="20" /></span><span>{{ label }}</span></div>
    <strong class="metric-value">{{ value }}</strong>
    <div class="progress-track"><span :style="{ width: `${Math.min(progress, 100)}%`, background: tone }" /></div>
    <span class="metric-hint">{{ hint }}</span>
  </article>
</template>
