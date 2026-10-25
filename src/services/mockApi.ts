import type { ChatMessage, MealPlan, MenuItem } from '../types'

/**
 * 演示环境的服务适配层。
 * 正式接入后端时保留公开函数签名，将内部实现替换为 HTTP/SSE 请求即可。
 */
const pause = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

/** 模拟视觉模型/OCR 的结构化菜单识别结果。 */
export async function recognizeMenu(): Promise<MenuItem[]> {
  await pause(1100)
  return [
    { id: 1, name: '糙米饭', price: 3, calories: [180, 230], protein: 4, vegetable: 0, allergens: [], confidence: 0.98 },
    { id: 2, name: '清蒸鸡腿', price: 10, calories: [210, 290], protein: 26, vegetable: 0, allergens: ['大豆'], confidence: 0.94 },
    { id: 3, name: '蒜蓉西兰花', price: 6, calories: [70, 120], protein: 4, vegetable: 160, allergens: [], confidence: 0.88 },
    { id: 4, name: '番茄炒蛋', price: 7, calories: [180, 260], protein: 11, vegetable: 90, allergens: ['蛋'], confidence: 0.96 },
    { id: 5, name: '香辣牛肉', price: 13, calories: [280, 390], protein: 24, vegetable: 30, allergens: ['大豆'], confidence: 0.72 },
  ]
}

/**
 * 根据已确认菜单与用户约束生成候选方案。
 * 模型只负责理解请求；正式版本中的价格、营养值和过敏约束应由后端工具校验。
 */
export async function buildPlans(items: MenuItem[], request = ''): Promise<MealPlan[]> {
  await pause(650)
  const lower = request.toLowerCase()
  const cheaper = lower.includes('便宜') || lower.includes('省钱')
  const noBeef = lower.includes('不要牛') || lower.includes('不吃牛')
  const noSpicy = lower.includes('不要辣') || lower.includes('不吃辣')
  const vegName = items.find((item) => item.name.includes('西兰花'))?.name ?? '时令蔬菜'
  const beefName = items.find((item) => item.name.includes('牛肉'))?.name
  const proteinName = noBeef || noSpicy ? '清蒸鸡腿' : beefName ?? '清蒸鸡腿'
  return [
    {
      id: 'balanced', title: '均衡优先', tag: '今日推荐', description: '主食、优质蛋白和蔬菜比例更完整',
      items: ['糙米饭', proteinName, vegName], price: cheaper ? 17 : 19, calories: [470, 640], protein: 34, vegetable: 160,
      match: 94, accent: '#247a52', reasons: ['覆盖三类主要食物', '蔬菜份量在当前方案中最高', '满足 25 元预算'],
    },
    {
      id: 'budget', title: '轻负担', tag: '省 ¥5', description: '控制预算的同时保留蛋白质与蔬菜',
      items: ['糙米饭', '番茄炒蛋', vegName], price: 16, calories: [430, 610], protein: 19, vegetable: 250,
      match: 88, accent: '#2f6ca4', reasons: ['价格最低', '不含辣味菜品', '蔬菜种类更丰富'],
    },
    {
      id: 'satisfying', title: '饱腹优先', tag: '高蛋白', description: '适合今天活动量较高时选择',
      items: ['糙米饭', proteinName, '番茄炒蛋'], price: 20, calories: [570, 780], protein: 41, vegetable: 90,
      match: 82, accent: '#a45c2f', reasons: ['蛋白质相对充足', '饱腹感更强', '蔬菜量相对不足，晚餐可补充'],
    },
  ]
}

// 演示知识库仅覆盖少量一般健康主题；未命中时必须明确拒绝无依据回答。
const answers: Record<string, { content: string; source: string; section: string }> = {
  早餐: {
    content: '早餐不必追求复杂，优先组合谷薯类、蛋白质来源和一种果蔬。例如全麦面包加鸡蛋和一份水果。若早晨时间紧，可以先保证两类，之后在加餐中补齐。',
    source: '中国居民膳食指南（2022）', section: '平衡膳食八准则',
  },
  饮水: {
    content: '可以把饮水分散到全天，小口、规律地补充。活动量增加或环境炎热时应适当增加。奶茶和含糖饮料不宜作为日常补水的主要来源。',
    source: '中国居民膳食指南（2022）', section: '足量饮水',
  },
  睡眠: {
    content: '规律的作息、睡前减少强光刺激以及避免较晚摄入咖啡因，通常有助于改善睡眠习惯。若失眠持续并影响日常生活，建议咨询专业医疗人员。',
    source: '健康中国行动（2019—2030年）', section: '健康环境促进行动',
  },
}

/** 从演示知识库生成带引用的回答，不进行疾病判断。 */
export async function askHealthAssistant(question: string): Promise<ChatMessage> {
  await pause(900)
  const found = Object.entries(answers).find(([keyword]) => question.includes(keyword))?.[1]
  const data = found ?? {
    content: '我可以提供一般性的饮食、饮水、活动和睡眠卫生知识。这个问题需要更多可靠资料才能给出有依据的回答，我不会根据不完整信息做医学判断。',
    source: '餐衡安全回答规范', section: '证据不足时的处理',
  }
  return {
    id: Date.now(), role: 'assistant', content: data.content,
    citations: [{ title: data.source, organization: data.source.includes('膳食') ? '中国营养学会' : '公开健康资料', section: data.section }],
  }
}
