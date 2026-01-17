<template>
  <div>
    <h2>消费&生产主题配置</h2>

    <div class="row mb-4">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5>主题配置列表</h5>
            <button class="btn btn-primary" @click="showAddForm = true; resetForm()">添加配置</button>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th>名称</th>
                    <th>关联MQTT配置</th>
                    <th>订阅主题</th>
                    <th>发布主题</th>
                    <th>解析配置</th>
                    <th>状态</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="config in configs" :key="config.id">
                    <td>{{ config.name }}</td>
                    <td>{{ mqttConfigName(config.mqtt_config_id) }}</td>
                    <td>
                      <div v-if="config.subscribe_topics">
                        <span 
                          v-for="topic in parseTopics(config.subscribe_topics)" 
                          :key="topic" 
                          class="badge bg-secondary me-1 mb-1"
                        >
                          {{ topic }}
                        </span>
                      </div>
                      <span v-else class="text-muted">无</span>
                    </td>
                    <td>{{ config.publish_topic || '-' }}</td>
                    <td>
                      <span v-if="config.json_parse_config" class="text-info" title="已配置JSON解析">
                        <i class="fas fa-code"></i> 已配置
                      </span>
                      <span v-else class="text-muted">默认解析</span>
                    </td>
                    <td>
                      <span :class="config.is_active ? 'text-success' : 'text-muted'">
                        {{ config.is_active ? '激活' : '未激活' }}
                      </span>
                    </td>
                    <td>
                      <button 
                        class="btn btn-sm btn-outline-primary me-1" 
                        @click="editConfig(config)"
                      >
                        编辑
                      </button>
                      <button 
                        class="btn btn-sm" 
                        :class="config.is_active ? 'btn-secondary' : 'btn-success'" 
                        @click="activateConfig(config)"
                        :disabled="config.is_active"
                      >
                        {{ config.is_active ? '当前激活' : '激活' }}
                      </button>
                      <button 
                        class="btn btn-sm btn-outline-danger" 
                        @click="deleteConfig(config.id)"
                      >
                        删除
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 配置编辑表单 -->
    <div class="row" v-if="showAddForm || editingConfig">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h5>{{ editingConfig ? '编辑配置' : '添加配置' }}</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="saveConfig">
              <div class="mb-3">
                <label for="name" class="form-label">配置名称 *</label>
                <input
                  type="text"
                  class="form-control"
                  id="name"
                  v-model="currentConfig.name"
                  :disabled="!!editingConfig"
                  required
                />
                <div class="form-text">配置名称必须唯一，用于区分不同主题配置</div>
              </div>
              
              <div class="mb-3">
                <label for="mqtt_config_id" class="form-label">关联MQTT配置 *</label>
                <select
                  class="form-control"
                  id="mqtt_config_id"
                  v-model.number="currentConfig.mqtt_config_id"
                  required
                >
                  <option value="" disabled>请选择MQTT配置</option>
                  <option 
                    v-for="mqttConfig in mqttConfigs" 
                    :key="mqttConfig.id" 
                    :value="mqttConfig.id"
                  >
                    {{ mqttConfig.name }} ({{ mqttConfig.server }}:{{ mqttConfig.port }})
                  </option>
                </select>
              </div>
              
              <div class="mb-3">
                <label for="subscribe_topics" class="form-label">订阅主题</label>
                <textarea
                  class="form-control"
                  id="subscribe_topics"
                  rows="3"
                  placeholder="每行一个主题，例如：device/+/temperature&#10;device/+/humidity"
                  v-model="currentConfig.subscribe_topics"
                ></textarea>
                <div class="form-text">每行一个订阅主题，支持通配符 (+ 和 #)</div>
              </div>
              
              <div class="mb-3">
                <label for="publish_topic" class="form-label">发布主题</label>
                <input
                  type="text"
                  class="form-control"
                  id="publish_topic"
                  placeholder="例如：commands/device1/control"
                  v-model="currentConfig.publish_topic"
                />
              </div>
              
              <div class="mb-3">
                <label for="json_parse_config" class="form-label">JSON 解析配置 (可选)</label>
                <div class="input-group mb-2">
                  <textarea
                    class="form-control"
                    id="json_parse_config"
                    rows="6"
                    placeholder='例如：{"air_temperature_1": {"type": "Temperature1", "unit": "°C"}, "air_humidity_1": {"type": "Humidity1", "unit": "%"}}'
                    v-model="currentConfig.json_parse_config"
                  ></textarea>
                </div>
                <div class="form-text">
                  <p class="mb-1">定义 JSON 数据的键如何映射到传感器类型和单位。</p>
                  <button type="button" class="btn btn-sm btn-outline-info" @click="showHelper = !showHelper">
                    {{ showHelper ? '隐藏工具' : '显示 JSON 配置助手' }}
                  </button>
                </div>
              </div>

              <!-- JSON 助手 -->
              <div v-if="showHelper" class="card mb-3 bg-light">
                <div class="card-body">
                  <h6>JSON 解析配置助手</h6>
                  <div class="mb-2">
                    <label class="form-label small">粘贴示例数据：</label>
                    <textarea class="form-control form-control-sm" rows="3" v-model="samplePayload" placeholder='{"temp": 25.5, "humi": 60}'></textarea>
                  </div>
                  <button type="button" class="btn btn-sm btn-secondary" @click="generateMapping">生成映射建议</button>
                  <div v-if="generatedMapping" class="mt-2">
                    <p class="small text-muted mb-1">建议配置：</p>
                    <pre class="bg-white p-2 small border rounded">{{ JSON.stringify(generatedMapping, null, 2) }}</pre>
                    <button type="button" class="btn btn-sm btn-success" @click="applyMapping">应用建议</button>
                  </div>
                </div>
              </div>
              
              <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                <button type="button" class="btn btn-secondary me-2" @click="showAddForm = false; editingConfig = null">
                  取消
                </button>
                <button type="submit" class="btn btn-primary">
                  {{ editingConfig ? '更新配置' : '保存配置' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card">
          <div class="card-header">
            <h5>配置说明</h5>
          </div>
          <div class="card-body">
            <h6>订阅主题</h6>
            <p>仪表盘将从这些主题消费数据，用于显示实时传感器数据。</p>
            
            <h6>发布主题</h6>
            <p>用于向设备发送控制命令或配置信息。</p>
            
            <h6>JSON 解析配置</h6>
            <p>当数据为 JSON 格式时，在此定义键名与传感器类型的映射关系。例如：<code>{"key": {"type": "Temperature1", "unit": "°C"}}</code></p>
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
  name: 'TopicConfig',
  setup() {
    const configs = ref([])
    const mqttConfigs = ref([])
    const showAddForm = ref(false)
    const editingConfig = ref(null)
    const showHelper = ref(false)
    const samplePayload = ref('')
    const generatedMapping = ref(null)
    const currentConfig = ref({
      id: null,
      name: '',
      mqtt_config_id: null,
      subscribe_topics: '',
      publish_topic: '',
      json_parse_config: ''
    })

    const loadConfigs = async () => {
      try {
        const response = await axios.get('/api/topic-configs')
        configs.value = response.data
      } catch (error) {
        console.error('加载主题配置失败:', error)
      }
    }

    const generateMapping = () => {
      try {
        const data = JSON.parse(samplePayload.value)
        const mapping = {}
        for (const key in data) {
          if (typeof data[key] === 'number') {
            let unit = ''
            let name = ''
            const keyLow = key.toLowerCase()
            
            // 自动识别单位和友好名称
            if (keyLow.includes('temp')) {
              unit = '°C'
              const num = key.match(/\d+/) ? key.match(/\d+/)[0] : ''
              name = num ? `温度${num}` : '温度'
            } else if (keyLow.includes('hum')) {
              unit = '%'
              const num = key.match(/\d+/) ? key.match(/\d+/)[0] : ''
              name = num ? `湿度${num}` : '湿度'
            } else if (keyLow.includes('relay')) {
              name = '继电器'
            }
            
            // 生成配置：始终保持原始 key 为 type 以保证唯一性和可区分性
            // 默认不设置 display_name，让用户在首页手动修改或在此手动指定
            mapping[key] = { 
              type: key, 
              unit: unit 
            }
          }
        }
        generatedMapping.value = mapping
      } catch (e) {
        alert('无法解析示例数据，请确保是有效的 JSON 格式')
      }
    }

    const applyMapping = () => {
      currentConfig.value.json_parse_config = JSON.stringify(generatedMapping.value, null, 2)
      showHelper.value = false
    }

    const loadMqttConfigs = async () => {
      try {
        const response = await axios.get('/api/mqtt-configs')
        mqttConfigs.value = Array.isArray(response.data) ? response.data : []
      } catch (error) {
        console.error('加载MQTT配置失败:', error)
        mqttConfigs.value = []
      }
    }

    const saveConfig = async () => {
      try {
        let response
        if (editingConfig.value) {
          // 更新现有配置
          response = await axios.put(`/api/topic-configs/${currentConfig.value.id}`, currentConfig.value)
        } else {
          // 创建新配置
          response = await axios.post('/api/topic-configs', currentConfig.value)
        }
        
        // 重新加载配置列表
        await loadConfigs()
        showAddForm.value = false
        editingConfig.value = null
      } catch (error) {
        console.error('保存主题配置失败:', error)
        alert(`保存失败: ${error.message}`)
      }
    }

    const editConfig = (config) => {
      // 如果subscribe_topics是JSON字符串，解析为换行分隔的字符串
      let subscribe_topics = config.subscribe_topics || ''
      try {
        const parsed = JSON.parse(subscribe_topics)
        if (Array.isArray(parsed)) {
          subscribe_topics = parsed.join('\n')
        }
      } catch (e) {
        // 如果不是JSON格式，保持原样
      }
      
      currentConfig.value = { 
        ...config,
        subscribe_topics: subscribe_topics,
        json_parse_config: config.json_parse_config || ''
      }
      editingConfig.value = config.id
      showAddForm.value = true
    }

    const deleteConfig = async (configId) => {
      if (!confirm('确定要删除这个主题配置吗？此操作不可撤销！')) {
        return
      }

      try {
        await axios.delete(`/api/topic-configs/${configId}`)
        await loadConfigs()
        alert('主题配置删除成功')
      } catch (error) {
        console.error('删除主题配置失败:', error)
        alert(`删除失败: ${error.message}`)
      }
    }

    const activateConfig = async (config) => {
      try {
        // 使用PUT请求更新配置的is_active状态，而不是专用的激活端点
        const updatedConfig = { ...config, is_active: true }
        await axios.put(`/api/topic-configs/${config.id}`, updatedConfig)
        await loadConfigs()
        alert(`配置 "${config.name}" 激活成功`)
      } catch (error) {
        console.error('激活主题配置失败:', error)
        alert(`激活失败: ${error.message}`)
      }
    }

    const mqttConfigName = (mqttConfigId) => {
      const config = mqttConfigs.value.find(c => c.id === mqttConfigId)
      return config ? config.name : '未知配置'
    }

    const parseTopics = (topicsStr) => {
      if (!topicsStr) return []
      try {
        // 尝试解析为JSON数组
        const parsed = JSON.parse(topicsStr)
        if (Array.isArray(parsed)) {
          return parsed
        }
      } catch (e) {
        // 如果不是JSON格式，则按换行符分割
        return topicsStr.split('\n').filter(t => t.trim() !== '')
      }
      return []
    }

    const resetForm = () => {
      currentConfig.value = {
        id: null,
        name: '',
        mqtt_config_id: null,
        subscribe_topics: '',
        publish_topic: '',
        json_parse_config: ''
      }
      editingConfig.value = null
      showHelper.value = false
      samplePayload.value = ''
      generatedMapping.value = null
    }

    onMounted(async () => {
      await Promise.all([
        loadConfigs(),
        loadMqttConfigs()
      ])
    })

    return {
      configs,
      mqttConfigs,
      showAddForm,
      editingConfig,
      showHelper,
      samplePayload,
      generatedMapping,
      currentConfig,
      saveConfig,
      editConfig,
      deleteConfig,
      activateConfig,
      mqttConfigName,
      parseTopics,
      resetForm,
      generateMapping,
      applyMapping
    }
  }
}
</script>