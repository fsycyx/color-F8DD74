// @vitest-environment jsdom

import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'
import { useHealthStore } from './health'
import type { MealPlan } from '../types'

const STORAGE_KEY = 'foodlens-health-v1'

const plan: MealPlan = {
  id: 'test-plan',
  title: '测试方案',
  tag: '测试',
  description: '独立测试数据',
  items: ['糙米饭', '西兰花'],
  price: 12,
  calories: [300, 400],
  protein: 15,
  vegetable: 160,
  match: 90,
  accent: '#247a52',
  reasons: ['覆盖主食与蔬菜'],
}

describe('health store persistence and boundaries', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('falls back to defaults and removes malformed JSON', () => {
    localStorage.setItem(STORAGE_KEY, '{invalid json')

    const store = useHealthStore()

    expect(store.today.water).toBe(1250)
    expect(store.today.sleep).toBe(7.1)
    expect(localStorage.getItem(STORAGE_KEY)).toBeNull()
  })

  it('restores valid persisted state', () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      today: { water: 900, sleep: 8, activity: 20, mood: '轻松', hunger: 2 },
      selectedPlan: plan,
      notifications: false,
    }))

    const store = useHealthStore()

    expect(store.today.water).toBe(900)
    expect(store.selectedPlan?.id).toBe('test-plan')
    expect(store.notifications).toBe(false)
  })

  it('updates the current week and caps progress at 100 percent', () => {
    const store = useHealthStore()

    store.addWater(800)
    store.today.activity = 90

    expect(store.today.water).toBe(2050)
    expect(store.week[6].water).toBe(2050)
    expect(store.waterPercent).toBe(100)
    expect(store.activityPercent).toBe(100)
  })

  it('persists nested changes and a selected meal plan', async () => {
    const store = useHealthStore()

    store.today.mood = '轻松'
    store.savePlan(plan)
    store.notifications = false
    await nextTick()

    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '{}')
    expect(saved.today.mood).toBe('轻松')
    expect(saved.selectedPlan.id).toBe('test-plan')
    expect(saved.notifications).toBe(false)
  })

  it('clears health values and the selected plan', () => {
    const store = useHealthStore()
    store.savePlan(plan)

    store.clearLocalData()

    expect(store.today).toEqual({ water: 0, sleep: 0, activity: 0, mood: '未记录', hunger: 3 })
    expect(store.selectedPlan).toBeNull()
  })
})
