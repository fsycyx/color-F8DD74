<script setup lang="ts">
import { nextTick, ref } from 'vue'
import { AlertTriangle, BookOpen, Bot, ExternalLink, LoaderCircle, Send, ShieldCheck, Sparkles, User } from 'lucide-vue-next'
import { askHealthAssistant } from '../services/mockApi'
import type { ChatMessage } from '../types'

const input = ref('')
const loading = ref(false)

// 首条消息主动声明能力边界，避免用户将一般健康信息误认为医疗建议。
const messages = ref<ChatMessage[]>([{ id: 1, role: 'assistant', content: '你好，我可以用公开、可靠的资料解释一般饮食、饮水、活动和睡眠知识。我不会进行疾病诊断，也不会替代医生或注册营养师。' }])
const chatEnd = ref<HTMLElement | null>(null)
const suggestions = ['早餐怎样搭配更均衡？', '白天应该怎样规律饮水？', '熬夜后第二天怎么安排饮食？']

async function scrollToLatestMessage() {
  await nextTick()
  chatEnd.value?.scrollIntoView({ behavior: 'smooth' })
}

async function send(text = input.value) {
  const question = text.trim()
  if (!question || loading.value) return

  messages.value.push({ id: Date.now(), role: 'user', content: question })
  input.value = ''
  loading.value = true
  await scrollToLatestMessage()

  try {
    messages.value.push(await askHealthAssistant(question))
  } catch {
    // 网络或模型异常时给出明确反馈，不能伪造正常的健康建议。
    messages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      content: '当前暂时无法核对可靠资料，请稍后重试。若问题涉及身体不适或疾病，请咨询专业医疗人员。',
    })
  } finally {
    loading.value = false
    await scrollToLatestMessage()
  }
}
</script>

<template>
  <section class="page assistant-page">
    <!-- 主栏负责对话，侧栏持续展示来源策略和医疗边界。 -->
    <div class="assistant-layout">
      <div class="chat-column">
        <div class="page-intro compact"><div><span class="eyebrow">有来源的健康知识</span><h2>AI 健康问答</h2><p>每条关键建议附带资料来源；证据不足时会明确说不知道。</p></div></div>
        <div class="chat-window">
          <div v-for="message in messages" :key="message.id" class="message" :class="message.role">
            <span class="message-avatar"><Bot v-if="message.role === 'assistant'" :size="19" /><User v-else :size="19" /></span>
            <div class="message-body"><p>{{ message.content }}</p><div v-if="message.citations?.length" class="citations"><span><BookOpen :size="15" />参考资料</span><button v-for="source in message.citations" :key="source.title" type="button"><div><strong>{{ source.title }}</strong><small>{{ source.organization }} · {{ source.section }}</small></div><ExternalLink :size="15" /></button></div></div>
          </div>
          <div v-if="loading" class="message assistant"><span class="message-avatar"><Bot :size="19" /></span><div class="typing"><i /><i /><i /><span>正在检索资料并核对边界</span></div></div>
          <div ref="chatEnd" />
        </div>
        <div class="suggestion-row"><button v-for="item in suggestions" :key="item" type="button" @click="send(item)"><Sparkles :size="14" />{{ item }}</button></div>
        <form class="chat-input" @submit.prevent="send()"><textarea v-model="input" rows="2" placeholder="问一个关于饮食、饮水、活动或睡眠的问题…" @keydown.enter.exact.prevent="send()" /><button class="primary-button" :disabled="!input.trim() || loading" aria-label="发送问题"><Send :size="19" /></button></form>
      </div>
      <aside class="assistant-sidebar">
        <article class="panel source-policy"><ShieldCheck :size="25" /><h3>回答原则</h3><ul><li>优先引用公开权威资料</li><li>区分事实、一般建议与不确定性</li><li>不根据少量信息推断疾病</li><li>不提供处方、用药或极端节食方案</li></ul></article>
        <article class="panel boundary-card"><AlertTriangle :size="22" /><div><h3>这些问题需要专业人员</h3><p>疾病饮食、孕产期、未成年人特殊营养、进食障碍、药物与饮食相互作用。</p></div></article>
      </aside>
    </div>
  </section>
</template>
