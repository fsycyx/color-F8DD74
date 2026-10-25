import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from './views/DashboardView.vue'

// 首屏只同步加载驾驶舱，其余业务页按路由懒加载以降低初始包体积。
const SmartMealView = () => import('./views/SmartMealView.vue')
const RecordsView = () => import('./views/RecordsView.vue')
const InsightsView = () => import('./views/InsightsView.vue')
const AssistantView = () => import('./views/AssistantView.vue')
const SettingsView = () => import('./views/SettingsView.vue')

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: DashboardView, meta: { title: '今日' } },
    { path: '/meal', component: SmartMealView, meta: { title: '智能点餐' } },
    { path: '/records', component: RecordsView, meta: { title: '健康记录' } },
    { path: '/insights', component: InsightsView, meta: { title: '趋势洞察' } },
    { path: '/assistant', component: AssistantView, meta: { title: 'AI 问答' } },
    { path: '/settings', component: SettingsView, meta: { title: '设置与隐私' } },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

router.afterEach((to) => {
  // 页面标题与当前业务模块保持同步，便于浏览器历史和无障碍导航识别。
  document.title = `${String(to.meta.title)} · 餐衡 FoodLens`
})
