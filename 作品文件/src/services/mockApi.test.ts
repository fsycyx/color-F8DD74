import { describe, expect, it } from 'vitest'
import { askHealthAssistant, buildPlans, recognizeMenu } from './mockApi'

// 服务适配层的契约测试：真实后端接入后也应保持这些行为不变。
describe('FoodLens mock service adapter', () => {
  it('returns editable recognized menu items', async () => {
    const items = await recognizeMenu()
    expect(items.length).toBeGreaterThanOrEqual(3)
    expect(items.every((item) => item.confidence > 0 && item.confidence <= 1)).toBe(true)
  })

  it('builds three plans within the demo budget', async () => {
    const plans = await buildPlans(await recognizeMenu(), '预算 25 元')
    expect(plans).toHaveLength(3)
    expect(plans.every((plan) => plan.price <= 25)).toBe(true)
    expect(plans.every((plan) => plan.reasons.length > 0)).toBe(true)
  })

  it('respects explicit non-spicy and no-beef constraints', async () => {
    const plans = await buildPlans(await recognizeMenu(), '不要辣，不吃牛肉')
    const selectedFoods = plans.flatMap((plan) => plan.items)

    expect(selectedFoods).not.toContain('香辣牛肉')
  })

  it('answers with citations and falls back safely', async () => {
    const known = await askHealthAssistant('早餐怎样搭配？')
    const unknown = await askHealthAssistant('请诊断我的疾病')
    expect(known.citations?.[0].title).toContain('膳食指南')
    expect(unknown.content).toContain('不会')
    expect(unknown.citations?.length).toBe(1)
  })
})
