<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="login-background">
      <div class="bg-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
      </div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-wrapper">
      <div class="login-card">
        <!-- Logo 区域 -->
        <div class="login-header">
          <div class="logo-container">
            <img src="/logo_center.png" alt="Logo" class="login-logo" />
          </div>
          <h1 class="login-title">MQTT IoT 管理系统</h1>
          <p class="login-subtitle">欢迎回来，请登录您的账户</p>
        </div>

        <!-- 登录表单 -->
        <div class="login-body">
          <form @submit.prevent="handleLogin" class="login-form">
            <div class="form-group">
              <label for="username" class="form-label">
                <i class="fas fa-user form-icon"></i>
                用户名
              </label>
              <div class="input-wrapper">
                <input
                  type="text"
                  class="form-input"
                  id="username"
                  v-model="username"
                  placeholder="请输入用户名"
                  required
                  :disabled="loading"
                  autocomplete="username"
                />
              </div>
            </div>

            <div class="form-group">
              <label for="password" class="form-label">
                <i class="fas fa-lock form-icon"></i>
                密码
              </label>
              <div class="input-wrapper">
                <input
                  type="password"
                  class="form-input"
                  id="password"
                  v-model="password"
                  placeholder="请输入密码"
                  required
                  :disabled="loading"
                  autocomplete="current-password"
                />
              </div>
            </div>

            <div v-if="error" class="error-message">
              <i class="fas fa-exclamation-circle me-2"></i>
              {{ error }}
            </div>

            <button 
              type="submit" 
              class="login-button"
              :disabled="loading"
            >
              <span v-if="loading" class="button-spinner">
                <span class="spinner-border spinner-border-sm" role="status"></span>
              </span>
              <span v-else class="button-content">
                <i class="fas fa-sign-in-alt me-2"></i>
                登录
              </span>
            </button>
          </form>
        </div>

        <!-- 底部提示 -->
        <div class="login-footer">
          <p class="footer-text">
            <i class="fas fa-shield-alt me-2"></i>
            安全登录，保护您的数据
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

export default {
  name: 'Login',
  setup() {
    const username = ref('')
    const password = ref('')
    const error = ref('')
    const loading = ref(false)
    const authStore = useAuthStore()
    const router = useRouter()

    const handleLogin = async () => {
      error.value = ''
      loading.value = true
      try {
        await authStore.login(username.value, password.value)
        // 获取用户信息
        await authStore.getCurrentUser()
        router.push('/dashboard')
      } catch (err) {
        error.value = err.message || '登录失败，请检查用户名和密码'
      } finally {
        loading.value = false
      }
    }

    return {
      username,
      password,
      error,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 200% 200%;
  animation: gradientShift 15s ease infinite;
  overflow: hidden;
  padding: 20px;
}

@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

/* 背景装饰 */
.login-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  z-index: 0;
}

.bg-shapes {
  position: relative;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  animation: float 20s infinite ease-in-out;
}

.shape-1 {
  width: 300px;
  height: 300px;
  background: #ffffff;
  top: -100px;
  right: -100px;
  animation-delay: 0s;
}

.shape-2 {
  width: 200px;
  height: 200px;
  background: #ffffff;
  bottom: -50px;
  left: -50px;
  animation-delay: 5s;
}

.shape-3 {
  width: 150px;
  height: 150px;
  background: #ffffff;
  top: 50%;
  left: 10%;
  animation-delay: 10s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -30px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

/* 登录卡片容器 */
.login-wrapper {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 450px;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.login-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 25px 70px rgba(0, 0, 0, 0.35);
}

/* 头部区域 */
.login-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 50px 30px 35px;
  text-align: center;
  color: white;
}

.logo-container {
  margin-bottom: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-logo {
  width: 200px;
  height: auto;
  max-width: 90%;
  filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.35));
  animation: logoFloat 3s ease-in-out infinite;
  transition: transform 0.3s ease;
}

.login-logo:hover {
  transform: scale(1.05);
}

@keyframes logoFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.login-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  letter-spacing: 1px;
}

.login-subtitle {
  font-size: 0.95rem;
  opacity: 0.9;
  margin: 0;
  font-weight: 300;
}

/* 表单区域 */
.login-body {
  padding: 40px 35px;
}

.login-form {
  width: 100%;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}

.form-icon {
  margin-right: 8px;
  color: #667eea;
  font-size: 0.85rem;
}

.input-wrapper {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 14px 16px;
  font-size: 1rem;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  background: #ffffff;
  transition: all 0.3s ease;
  outline: none;
}

.form-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  background: #f8f9ff;
}

.form-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
  opacity: 0.7;
}

.form-input::placeholder {
  color: #adb5bd;
}

/* 错误提示 */
.error-message {
  background: #fee;
  border: 1px solid #fcc;
  color: #c33;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  animation: shake 0.5s ease;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-10px);
  }
  75% {
    transform: translateX(10px);
  }
}

/* 登录按钮 */
.login-button {
  width: 100%;
  padding: 16px;
  font-size: 1.1rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  position: relative;
  overflow: hidden;
}

.login-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.login-button:hover::before {
  left: 100%;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.login-button:active {
  transform: translateY(0);
}

.login-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.button-content,
.button-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 底部区域 */
.login-footer {
  padding: 20px 35px;
  background: #f8f9fa;
  text-align: center;
  border-top: 1px solid #e9ecef;
}

.footer-text {
  margin: 0;
  font-size: 0.85rem;
  color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    padding: 15px;
  }

  .login-card {
    border-radius: 20px;
  }

  .login-header {
    padding: 30px 20px;
  }

  .login-title {
    font-size: 1.5rem;
  }

  .login-body {
    padding: 30px 25px;
  }

  .login-logo {
    width: 140px;
  }

  .shape {
    display: none;
  }
}

@media (max-width: 480px) {
  .login-header {
    padding: 35px 15px 25px;
  }

  .login-body {
    padding: 25px 20px;
  }

  .login-title {
    font-size: 1.3rem;
  }

  .login-subtitle {
    font-size: 0.85rem;
  }

  .login-logo {
    width: 120px;
  }
}
</style>