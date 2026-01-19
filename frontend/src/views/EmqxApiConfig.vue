<template>
  <div>
    <h2>EMQX API 配置</h2>
    <p class="text-muted">配置 EMQX REST API 访问密钥，用于获取客户端连接状态等信息</p>

    <div class="row">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h5>API 密钥配置</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="saveConfig">
              <div class="mb-3">
                <label for="api_port" class="form-label">API 端口</label>
                <input
                  type="number"
                  class="form-control"
                  id="api_port"
                  v-model.number="config.api_port"
                  required
                  min="1"
                  max="65535"
                />
                <div class="form-text">EMQX 管理 API 端口，默认为 18083</div>
              </div>

              <div class="mb-3">
                <label for="api_key" class="form-label">API Key *</label>
                <input
                  type="text"
                  class="form-control"
                  id="api_key"
                  v-model="config.api_key"
                  required
                  placeholder="例如: f3d064c3dacad617"
                />
                <div class="form-text">在 EMQX Dashboard 的"系统设置 -> API 密钥"中创建</div>
              </div>

              <div class="mb-3">
                <label for="api_secret" class="form-label">Secret Key *</label>
                <input
                  type="password"
                  class="form-control"
                  id="api_secret"
                  v-model="config.api_secret"
                  required
                  placeholder="输入 Secret Key"
                />
                <div class="form-text">创建 API Key 时生成的密钥</div>
              </div>

              <div class="alert alert-info">
                <h6><i class="fas fa-info-circle"></i> 如何获取 API Key？</h6>
                <ol class="mb-0">
                  <li>访问 EMQX Dashboard (默认: <code>http://localhost:18083</code>)</li>
                  <li>进入"系统设置" -> "API 密钥"</li>
                  <li>点击"创建"按钮</li>
                  <li>复制生成的 API Key 和 Secret Key</li>
                </ol>
                <div class="mt-2">
                  <a href="https://docs.emqx.com/zh/emqx/v5.2/admin/api.html" target="_blank" class="btn btn-sm btn-outline-primary">
                    <i class="fas fa-external-link-alt"></i> 查看官方文档
                  </a>
                </div>
              </div>

              <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                <button type="button" class="btn btn-outline-secondary me-2" @click="testConnection" :disabled="isTesting">
                  <span v-if="isTesting">
                    <span class="spinner-border spinner-border-sm me-1"></span>
                    测试中...
                  </span>
                  <span v-else>
                    <i class="fas fa-plug"></i> 测试连接
                  </span>
                </button>
                <button type="submit" class="btn btn-primary" :disabled="isSaving">
                  <span v-if="isSaving">
                    <span class="spinner-border spinner-border-sm me-1"></span>
                    保存中...
                  </span>
                  <span v-else>
                    <i class="fas fa-save"></i> 保存配置
                  </span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <!-- 连接状态 -->
        <div class="card">
          <div class="card-header">
            <h5>连接状态</h5>
          </div>
          <div class="card-body">
            <div v-if="testResult.tested" class="alert" :class="testResult.success ? 'alert-success' : 'alert-danger'">
              <h6>
                <i class="fas" :class="testResult.success ? 'fa-check-circle' : 'fa-times-circle'"></i>
                {{ testResult.success ? '连接成功' : '连接失败' }}
              </h6>
              <p class="mb-0">{{ testResult.message }}</p>
              <small class="text-muted">{{ formatDate(testResult.timestamp) }}</small>
            </div>
            <div v-else class="text-muted text-center py-3">
              <i class="fas fa-question-circle fa-2x mb-2"></i>
              <p>尚未测试连接</p>
            </div>

            <div v-if="testResult.success && testResult.clientCount !== null" class="mt-3">
              <h6>当前连接信息</h6>
              <ul class="list-group list-group-flush">
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  客户端总数
                  <span class="badge bg-primary rounded-pill">{{ testResult.clientCount }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 配置说明 -->
        <div class="card mt-3">
          <div class="card-header">
            <h5>功能说明</h5>
          </div>
          <div class="card-body">
            <h6>配置用途</h6>
            <ul>
              <li>实时获取设备在线/离线状态</li>
              <li>在 Dashboard 首页显示统计信息</li>
              <li>查看客户端连接详情</li>
            </ul>

            <h6 class="mt-3">安全提示</h6>
            <ul class="text-muted small mb-0">
              <li>API Key 具有管理权限，请妥善保管</li>
              <li>建议为本应用单独创建 API Key</li>
              <li>定期更换 API 密钥以保证安全</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'EmqxApiConfig',
  setup() {
    const config = ref({
      api_port: 18083,
      api_key: '',
      api_secret: ''
    })

    const testResult = ref({
      tested: false,
      success: false,
      message: '',
      timestamp: null,
      clientCount: null
    })

    const isSaving = ref(false)
    const isTesting = ref(false)

    // 加载配置
    const loadConfig = async () => {
      try {
        const response = await axios.get('/api/emqx-api-config')
        if (response.data) {
          config.value = {
            api_port: response.data.api_port || 18083,
            api_key: response.data.api_key || '',
            api_secret: response.data.api_secret || ''
          }
        }
      } catch (error) {
        console.error('加载配置失败:', error)
        // 如果是 404 错误，说明还没有配置，这是正常的
        if (error.response?.status !== 404) {
          alert('加载配置失败: ' + (error.response?.data?.detail || error.message))
        }
      }
    }

    // 保存配置
    const saveConfig = async () => {
      if (!config.value.api_key || !config.value.api_secret) {
        alert('请填写 API Key 和 Secret Key')
        return
      }

      isSaving.value = true
      try {
        await axios.post('/api/emqx-api-config', config.value)
        alert('配置保存成功！')
        
        // 保存成功后自动测试连接
        await testConnection()
      } catch (error) {
        console.error('保存配置失败:', error)
        alert('保存配置失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        isSaving.value = false
      }
    }

    // 测试连接
    const testConnection = async () => {
      if (!config.value.api_key || !config.value.api_secret) {
        alert('请先填写 API Key 和 Secret Key')
        return
      }

      isTesting.value = true
      testResult.value = {
        tested: false,
        success: false,
        message: '',
        timestamp: null,
        clientCount: null
      }

      try {
        const response = await axios.post('/api/emqx-api-config/test', config.value)
        testResult.value = {
          tested: true,
          success: true,
          message: response.data.message || '连接成功',
          timestamp: new Date(),
          clientCount: response.data.client_count || 0
        }
      } catch (error) {
        console.error('测试连接失败:', error)
        testResult.value = {
          tested: true,
          success: false,
          message: error.response?.data?.detail || error.message || '连接失败',
          timestamp: new Date(),
          clientCount: null
        }
      } finally {
        isTesting.value = false
      }
    }

    const formatDate = (date) => {
      if (!date) return ''
      return new Date(date).toLocaleString('zh-CN')
    }

    onMounted(() => {
      loadConfig()
    })

    return {
      config,
      testResult,
      isSaving,
      isTesting,
      saveConfig,
      testConnection,
      formatDate
    }
  }
}
</script>

<style scoped>
.card {
  margin-bottom: 20px;
}

code {
  color: #d63384;
  background-color: #f8f9fa;
  padding: 2px 6px;
  border-radius: 3px;
}
</style>
