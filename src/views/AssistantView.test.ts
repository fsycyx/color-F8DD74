// @vitest-environment jsdom

import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import AssistantView from './AssistantView.vue'
import { askHealthAssistant } from '../services/mockApi'

vi.mock('../services/mockApi', () => ({ askHealthAssistant: vi.fn() }))

describe('AssistantView request handling', () => {
  beforeEach(() => {
    vi.mocked(askHealthAssistant).mockReset()
    Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', { configurable: true, value: vi.fn() })
  })

  it('renders an answer and its traceable citation', async () => {
    vi.mocked(askHealthAssistant).mockResolvedValue({
      id: 2,
      role: 'assistant',
      content: '把饮水分散到全天。',
      citations: [{ title: '中国居民膳食指南（2022）', organization: '中国营养学会', section: '足量饮水' }],
    })
    const wrapper = mount(AssistantView)

    await wrapper.get('textarea').setValue('饮水建议')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(askHealthAssistant).toHaveBeenCalledWith('饮水建议')
    expect(wrapper.text()).toContain('把饮水分散到全天')
    expect(wrapper.text()).toContain('中国居民膳食指南')
  })

  it('shows a safe fallback when the adapter rejects', async () => {
    vi.mocked(askHealthAssistant).mockRejectedValue(new Error('network unavailable'))
    const wrapper = mount(AssistantView)

    await wrapper.get('textarea').setValue('请回答')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('当前暂时无法核对可靠资料')
    expect(wrapper.text()).toContain('请咨询专业医疗人员')
  })
})
