import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { router } from './router'
import './styles.css'

// 应用级插件在入口统一注册，业务组件不直接创建全局实例。
createApp(App).use(createPinia()).use(router).mount('#app')
