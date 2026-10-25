// @vitest-environment jsdom

import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import SmartMealView from './SmartMealView.vue'
import { buildPlans, recognizeMenu } from '../services/mockApi'

vi.mock('../services/mockApi', () => ({
  recognizeMenu: vi.fn(),
  buildPlans: vi.fn(),
}))

const menuItems = [
  { id: 1, name: '糙米饭', price: 3, calories: [180, 230] as [number, number], protein: 4, vegetable: 0, allergens: [], confidence: 0.98 },
  { id: 2, name: '西兰花', price: 6, calories: [70, 120] as [number, number], protein: 4, vegetable: 160, allergens: [], confidence: 0.72 },
]

const plans = [{
  id: 'balanced', title: '均衡优先', tag: '推荐', description: '测试方案', items: ['糙米饭', '西兰花'],
  price: 9, calories: [250, 350] as [number, number], protein: 8, vegetable: 160, match: 90, accent: '#247a52', reasons: ['蔬菜充足'],
}]

describe('SmartMealView workflow', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    vi.mocked(recognizeMenu).mockResolvedValue(menuItems)
    vi.mocked(buildPlans).mockResolvedValue(plans)
    Object.defineProperty(URL, 'createObjectURL', { configurable: true, value: vi.fn(() => 'blob:test-menu') })
    Object.defineProperty(URL, 'revokeObjectURL', { configurable: true, value: vi.fn() })
  })

  it('rejects analysis when no image has been selected', async () => {
    const wrapper = mount(SmartMealView)

    await wrapper.get('button.primary-button.full').trigger('click')

    expect(wrapper.text()).toContain('请先选择一张菜单图片或截图')
    expect(recognizeMenu).not.toHaveBeenCalled()
  })

  it('moves through upload, review, planning, and explicit selection', async () => {
    const wrapper = mount(SmartMealView)
    const input = wrapper.get('input[type="file"]')
    Object.defineProperty(input.element, 'files', {
      configurable: true,
      value: [new File(['menu'], 'menu.png', { type: 'image/png' })],
    })

    await input.trigger('change')
    await wrapper.get('button.primary-button.full').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('平均置信度 85%')
    expect(wrapper.text()).toContain('请确认菜名与价格')

    await wrapper.get('button.primary-button.full').trigger('click')
    await flushPromises()

    expect(buildPlans).toHaveBeenCalledOnce()
    expect(wrapper.text()).toContain('均衡优先')

    await wrapper.get('.plan-button').trigger('click')
    expect(wrapper.text()).toContain('已加入今日记录')
  })
})
