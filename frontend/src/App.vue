<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark" v-if="authStore.isAuthenticated">
      <div class="container-fluid">
        <a class="navbar-brand" href="/">MQTT IoT 管理系统</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <nav class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <router-link class="nav-link" to="/dashboard">首页</router-link>
            </li>
            <li class="nav-item" v-if="authStore.isAdmin">
              <router-link class="nav-link" to="/devices">设备管理</router-link>
            </li>
            <li class="nav-item" v-if="authStore.isAdmin">
              <router-link class="nav-link" to="/realtime-data">实时数据</router-link>
            </li>
            <li class="nav-item" v-if="authStore.isAdmin">
              <router-link class="nav-link" to="/mqtt-config">MQTT配置管理</router-link>
            </li>
            <li class="nav-item" v-if="authStore.isAdmin">
              <router-link class="nav-link" to="/topic-config">消费&生产主题配置</router-link>
            </li>
            <li class="nav-item" v-if="authStore.isAdmin">
              <router-link class="nav-link" to="/subscribe-options">订阅选项</router-link>
            </li>
            <li class="nav-item" v-if="authStore.isAdmin">
              <router-link class="nav-link" to="/users">用户管理</router-link>
            </li>
          </nav>
          <div class="navbar-nav ms-auto">
            <li class="nav-item dropdown" v-if="authStore.user">
              <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
                <i class="fas fa-user me-1"></i>
                {{ authStore.user.username }}
                <span v-if="authStore.isAdmin" class="badge bg-warning ms-1">管理员</span>
              </a>
              <ul class="dropdown-menu dropdown-menu-end">
                <li>
                  <a class="dropdown-item" href="#" @click.prevent="handleLogout">
                    <i class="fas fa-sign-out-alt me-2"></i>退出登录
                  </a>
                </li>
              </ul>
            </li>
          </div>
        </div>
      </div>
    </nav>
    <div class="container-fluid" v-if="authStore.isAuthenticated">
      <router-view></router-view>
    </div>
    <router-view v-else></router-view>
  </div>
</template>

<script>
import { RouterView, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

export default {
  name: 'App',
  components: {
    RouterView
  },
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    
    const handleLogout = () => {
      authStore.logout()
      router.push('/login')
    }
    
    return {
      authStore,
      handleLogout
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>