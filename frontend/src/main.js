import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

// 引入Bootstrap CSS（使用本地安装的版本）
import 'bootstrap/dist/css/bootstrap.min.css'
// 引入Bootstrap JS（如果需要使用Bootstrap的JavaScript功能）
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// 配置axios基础URL，使用相对路径以便Vite代理能正确处理请求
import axios from 'axios'
// 使用相对路径，这样Vite代理可以正确转发请求到后端
axios.defaults.baseURL = '/'

// 请求拦截器：在每个请求中添加JWT令牌，并统一处理API路径
axios.interceptors.request.use(
  (config) => {
    // 添加JWT令牌
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 统一处理API路径：将 /api/* 重写为 /api/v1/*（如果路径不是 /api/v1/*）
    // 这样可以在开发环境（Vite代理）和生产环境（直接访问）中都正常工作
    if (config.url && config.url.startsWith('/api/') && !config.url.startsWith('/api/v1/')) {
      // 重写路径：/api/* -> /api/v1/*
      config.url = '/api/v1' + config.url.substring(4);
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理认证错误
axios.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // 认证失败，重定向到登录页面
      localStorage.removeItem('token');
      window.location.href = '/#/login';
    }
    return Promise.reject(error);
  }
);

// 创建Vue应用
const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')