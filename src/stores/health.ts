import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'
import type { DayPoint, HealthLog, MealPlan } from '../types'

const STORAGE_KEY = 'foodlens-health-v1'
const DEFAULT_HEALTH_LOG: HealthLog = {
  water: 1250,
  sleep: 7.1,
  activity: 32,
  mood: '平稳',
  hunger: 3,
}

const weekSeed: DayPoint[] = [
  { day: '周一', water: 1300, sleep: 6.4, activity: 25, vegetables: 280 },
  { day: '周二', water: 1800, sleep: 7.2, activity: 42, vegetables: 360 },
  { day: '周三', water: 1500, sleep: 6.8, activity: 30, vegetables: 310 },
  { day: '周四', water: 2100, sleep: 7.5, activity: 48, vegetables: 420 },
  { day: '周五', water: 1650, sleep: 6.1, activity: 22, vegetables: 260 },
  { day: '周六', water: 1900, sleep: 8.0, activity: 55, vegetables: 390 },
  { day: '今天', water: 1250, sleep: 7.1, activity: 32, vegetables: 220 },
]

export const useHealthStore = defineStore('health', () => {
  // localStorage 可能被用户手动修改，读取失败时必须回退到安全的演示数据。
  let parsed: { today?: HealthLog; selectedPlan?: MealPlan; notifications?: boolean } | null = null
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    parsed = saved ? JSON.parse(saved) : null
  } catch {
    localStorage.removeItem(STORAGE_KEY)
  }

  const today = ref<HealthLog>(parsed?.today ?? { ...DEFAULT_HEALTH_LOG })
  const selectedPlan = ref<MealPlan | null>(parsed?.selectedPlan ?? null)
  const notifications = ref(parsed?.notifications ?? true)
  const week = ref<DayPoint[]>(weekSeed)

  const waterPercent = computed(() => Math.min(100, Math.round((today.value.water / 1800) * 100)))
  const activityPercent = computed(() => Math.min(100, Math.round((today.value.activity / 45) * 100)))

  function addWater(amount: number) {
    today.value.water += amount
    week.value[6].water = today.value.water
  }

  function savePlan(plan: MealPlan) {
    selectedPlan.value = plan
  }

  function clearLocalData() {
    localStorage.removeItem(STORAGE_KEY)
    today.value = { water: 0, sleep: 0, activity: 0, mood: '未记录', hunger: 3 }
    selectedPlan.value = null
  }

  // 深度监听确保滑杆、快捷记录等嵌套字段变化后也能即时持久化。
  watch(
    [today, selectedPlan, notifications],
    () => {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          today: today.value,
          selectedPlan: selectedPlan.value,
          notifications: notifications.value,
        }),
      )
    },
    { deep: true },
  )

  return { today, selectedPlan, notifications, week, waterPercent, activityPercent, addWater, savePlan, clearLocalData }
})
