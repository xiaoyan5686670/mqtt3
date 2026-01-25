import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => {
    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')
    return {
      user: userStr ? JSON.parse(userStr) : null,
      token: token,
      isAuthenticated: !!token
    }
  },

  getters: {
    isAdmin: (state) => {
      return state.user?.is_admin === true
    },
    canEdit: (state) => {
      // 只要登录了就可以编辑（API会控制只能看到自己的设备，或者管理员能看到所有）
      return !!state.user
    }
  },

  actions: {
    async login(username, password) {
      try {
        const formData = new FormData()
        formData.append('username', username)
        formData.append('password', password)
        
        const response = await axios.post('/api/auth/login', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        })
        
        if (response.data.access_token) {
          this.token = response.data.access_token
          this.user = response.data.user
          this.isAuthenticated = true
          localStorage.setItem('token', this.token)
          localStorage.setItem('user', JSON.stringify(this.user))
          return { success: true }
        } else {
          throw new Error('登录失败：未收到访问令牌')
        }
      } catch (error) {
        const message = error.response?.data?.detail || error.message || '登录失败'
        throw new Error(message)
      }
    },

    async getCurrentUser() {
      try {
        const response = await axios.get('/api/auth/me')
        this.user = response.data
        localStorage.setItem('user', JSON.stringify(this.user))
        return this.user
      } catch (error) {
        // 如果获取用户信息失败，清除认证状态
        this.logout()
        throw error
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})