import { afterEach, describe, expect, it, vi } from 'vitest'
import { askHealthAssistant, buildPlans, recognizeMenu } from './mockApi'

afterEach(() => {
  vi.useRealTimers()
})

async function finishDelay<T>(pending: Promise<T>) {
  await vi.runAllTimersAsync()
  return pending
}

describe('FoodLens mock adapter branches', () => {
  it('applies the cheaper request branch without exceeding the regular price', async () => {
    vi.useFakeTimers()
    const items = await finishDelay(recognizeMenu())
    const regular = await finishDelay(buildPlans(items))
    const cheaper = await finishDelay(buildPlans(items, '想省钱一点'))

    expect(cheaper[0].price).toBeLessThan(regular[0].price)
    expect(cheaper.every((item) => item.price <= 25)).toBe(true)
  })

  it('uses the non-beef protein branch for both supported constraint phrases', async () => {
    vi.useFakeTimers()
    const items = await finishDelay(recognizeMenu())

    for (const request of ['不要牛肉', '不吃辣']) {
      const plans = await finishDelay(buildPlans(items, request))
      expect(plans.flatMap((item) => item.items)).not.toContain('香辣牛肉')
      expect(plans[0].items).toContain('清蒸鸡腿')
    }
  })

  it.each([
    ['饮水', '足量饮水'],
    ['睡眠', '健康环境促进行动'],
  ])('returns a traceable citation for the %s knowledge branch', async (keyword, section) => {
    vi.useFakeTimers()
    const answer = await finishDelay(askHealthAssistant(`请介绍${keyword}建议`))

    expect(answer.role).toBe('assistant')
    expect(answer.citations?.[0].section).toContain(section)
  })
})
