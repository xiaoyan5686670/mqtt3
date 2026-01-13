import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Dashboard from '../views/Dashboard.vue'
import DeviceList from '../views/DeviceList.vue'
import DeviceDetail from '../views/DeviceDetail.vue'
import DeviceEdit from '../views/DeviceEdit.vue'
import MqttConfig from '../views/MqttConfig.vue'
import TopicConfig from '../views/TopicConfig.vue'
import RealTimeData from '../views/RealTimeData.vue'
import Login from '../views/Login.vue'
import SubscribeOptions from '../views/SubscribeOptions.vue'
import UserList from '../views/UserList.vue'
import UserEdit from '../views/UserEdit.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/devices',
    name: 'DeviceList',
    component: DeviceList,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/devices/:id',
    name: 'DeviceDetail',
    component: DeviceDetail,
    props: true,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/devices/new',
    name: 'DeviceNew',
    component: DeviceEdit,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/devices/:id/edit',
    name: 'DeviceEdit',
    component: DeviceEdit,
    props: true,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/realtime-data',
    name: 'RealTimeData',
    component: RealTimeData,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/mqtt-config',
    name: 'MqttConfig',
    component: MqttConfig,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/topic-config',
    name: 'TopicConfig',
    component: TopicConfig,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/subscribe-options',
    name: 'SubscribeOptions',
    component: SubscribeOptions,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/users',
    name: 'UserList',
    component: UserList,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/users/new',
    name: 'UserNew',
    component: UserEdit,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/users/:id/edit',
    name: 'UserEdit',
    component: UserEdit,
    props: true,
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 如果路由需要认证
  if (to.meta.requiresAuth) {
    // 检查是否有token
    if (!authStore.token) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    
    // 如果没有用户信息，尝试获取
    if (!authStore.user) {
      try {
        await authStore.getCurrentUser()
      } catch (error) {
        // 获取用户信息失败，跳转到登录页
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
    }
    
    // 检查是否需要管理员权限
    if (to.meta.requiresAdmin && !authStore.isAdmin) {
      // 普通用户只能访问首页
      if (to.name !== 'Dashboard') {
        next({ name: 'Dashboard' })
        return
      }
    }
  }
  
  // 如果已登录用户访问登录页，重定向到首页
  if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
    return
  }
  
  next()
})

export default router