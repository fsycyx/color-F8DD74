/** 菜单识别后的标准化菜品，营养值均来自数据库估算而非模型直接生成。 */
export interface MenuItem {
  id: number
  name: string
  price: number
  calories: [number, number]
  protein: number
  vegetable: number
  allergens: string[]
  confidence: number
  selected?: boolean
}

/** Agent 在预算、偏好和健康约束下生成的候选点餐方案。 */
export interface MealPlan {
  id: string
  title: string
  tag: string
  description: string
  items: string[]
  price: number
  calories: [number, number]
  protein: number
  vegetable: number
  match: number
  accent: string
  reasons: string[]
}

/** 用户当天主动记录的健康上下文，不作为医疗档案使用。 */
export interface HealthLog {
  water: number
  sleep: number
  activity: number
  mood: string
  hunger: number
}

/** 趋势页使用的单日聚合数据。 */
export interface DayPoint {
  day: string
  water: number
  sleep: number
  activity: number
  vegetables: number
}

/** AI 回答所引用的可追溯资料。 */
export interface Citation {
  title: string
  organization: string
  section: string
}

/** 健康问答中的单条消息。 */
export interface ChatMessage {
  id: number
  role: 'assistant' | 'user'
  content: string
  citations?: Citation[]
}
