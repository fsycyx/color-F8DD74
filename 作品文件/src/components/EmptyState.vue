<script setup lang="ts">
import { Inbox } from 'lucide-vue-next'

/** 列表或计算结果为空时的统一反馈。 */
defineProps<{ title: string; detail: string }>()
</script>

<template>
  <div class="empty-state"><Inbox :size="28" /><strong>{{ title }}</strong><span>{{ detail }}</span></div>
</template>
