<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <router-link to="/dashboard">仪表板</router-link>
        </li>
        <li class="breadcrumb-item">
          <router-link to="/devices">设备列表</router-link>
        </li>
        <li class="breadcrumb-item active" aria-current="page">{{ isEditing ? '编辑设备' : '添加设备' }}</li>
      </ol>
    </nav>

    <div class="card">
      <div class="card-header">
        <h3>{{ isEditing ? '编辑设备' : '添加设备' }}</h3>
      </div>
      <div class="card-body">
        <form @submit.prevent="saveDevice">
          <div class="mb-3">
            <label for="deviceName" class="form-label">设备名称 *</label>
            <input
              type="text"
              class="form-control"
              id="deviceName"
              v-model="deviceForm.name"
              required
            />
          </div>
          
          <div class="mb-3">
            <label for="deviceType" class="form-label">设备类型 *</label>
            <input
              type="text"
              class="form-control"
              id="deviceType"
              v-model="deviceForm.device_type"
              required
            />
          </div>
          
          <div class="mb-3">
            <label for="deviceLocation" class="form-label">设备位置</label>
            <input
              type="text"
              class="form-control"
              id="deviceLocation"
              v-model="deviceForm.location"
            />
          </div>
          
          <div class="mb-3">
            <label for="clientId" class="form-label">客户端 ID (Client ID)</label>
            <input
              type="text"
              class="form-control"
              id="clientId"
              v-model="deviceForm.clientid"
              placeholder="EMQX 客户端 ID，用于判断设备在线状态"
            />
            <div class="form-text">设备在 EMQX 中的客户端 ID，用于准确判断设备在线状态。如果不填写，默认使用设备名称。</div>
          </div>
          
          <div class="mb-3">
            <label for="deviceRemark" class="form-label">备注</label>
            <textarea
              class="form-control"
              id="deviceRemark"
              v-model="deviceForm.remark"
              rows="3"
              placeholder="可在此填写设备相关备注信息"
            ></textarea>
            <div class="form-text">用于记录设备的相关信息，如设备位置、用途等</div>
          </div>
          
          <div class="mb-3">
            <div class="form-check">
              <input
                class="form-check-input"
                type="checkbox"
                id="showOnDashboard"
                v-model="deviceForm.show_on_dashboard"
              />
              <label class="form-check-label" for="showOnDashboard">
                在首页展示
              </label>
            </div>
            <div class="form-text">勾选后，该设备将在首页仪表板中显示</div>
          </div>
          
          <div class="mb-3">
            <label for="mqttConfig" class="form-label">MQTT配置</label>
            <select
              class="form-control"
              id="mqttConfig"
              v-model="deviceForm.mqtt_config_id"
            >
              <option value="">请选择MQTT配置</option>
              <option v-for="config in mqttConfigs" :key="config.id" :value="config.id">
                {{ config.name }} ({{ config.server }}:{{ config.port }})
              </option>
            </select>
            <div class="form-text">选择用于此设备通信的MQTT配置</div>
          </div>
          
          <div class="mb-3">
            <label for="topicConfig" class="form-label">主题配置</label>
            <select
              class="form-control"
              id="topicConfig"
              v-model="deviceForm.topic_config_id"
            >
              <option value="">请选择主题配置</option>
              <option v-for="config in topicConfigs" :key="config.id" :value="config.id">
                {{ config.name }}
              </option>
            </select>
            <div class="form-text">选择用于此设备数据订阅/发布的主题配置</div>
          </div>

          <!-- 继电器控制消息格式配置 -->
          <div class="card mb-3 bg-light">
            <div class="card-body">
              <h6 class="card-title">
                <i class="fas fa-toggle-on me-2"></i>继电器控制消息格式配置（可选）
              </h6>
              <p class="text-muted small mb-3">为此设备单独配置继电器开关的消息格式。如果不配置，将使用主题配置中的默认格式。</p>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="relayOnPayload" class="form-label">继电器开启消息</label>
                  <input
                    type="text"
                    class="form-control"
                    id="relayOnPayload"
                    placeholder='例如：relayon 或 {"relay":"on"}'
                    v-model="deviceForm.relay_on_payload"
                  />
                  <div class="form-text">
                    留空则使用主题配置或默认值 "relayon"
                  </div>
                </div>
                
                <div class="col-md-6 mb-3">
                  <label for="relayOffPayload" class="form-label">继电器关闭消息</label>
                  <input
                    type="text"
                    class="form-control"
                    id="relayOffPayload"
                    placeholder='例如：relayoff 或 {"relay":"off"}'
                    v-model="deviceForm.relay_off_payload"
                  />
                  <div class="form-text">
                    留空则使用主题配置或默认值 "relayoff"
                  </div>
                </div>
              </div>

              <div class="alert alert-info mb-0 small">
                <i class="fas fa-info-circle me-1"></i>
                <strong>提示：</strong>
                <ul class="mb-0 mt-1">
                  <li>优先级：设备配置 &gt; 主题配置 &gt; 系统默认值</li>
                  <li>字符串格式示例：<code>relayon</code>、<code>1</code>、<code>ON</code></li>
                  <li>JSON格式示例：<code>{"relay":"on"}</code>、<code>{"cmd":"relay","value":1}</code></li>
                  <li>如果此设备的下位机使用特殊格式，在此配置；否则留空使用通用配置</li>
                </ul>
              </div>
            </div>
          </div>
          
          <div class="d-grid gap-2 d-md-flex justify-content-md-end">
            <router-link to="/devices" class="btn btn-secondary me-2">取消</router-link>
            <button type="submit" class="btn btn-primary">
              {{ isEditing ? '更新设备' : '添加设备' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

export default {
  name: 'DeviceEdit',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const isEditing = ref(!!route.params.id)
    const mqttConfigs = ref([])
    const topicConfigs = ref([])
    
    const deviceForm = ref({
      name: '',
      device_type: '',  // 改为与后端API匹配的字段名
      location: '',
      clientid: '',  // EMQX 客户端 ID
      remark: '',  // 备注字段
      show_on_dashboard: true,  // 是否在首页展示，默认true
      mqtt_config_id: null,
      topic_config_id: null,
      relay_on_payload: '',  // 继电器开启payload
      relay_off_payload: ''  // 继电器关闭payload
    })

    // 加载MQTT配置列表
    const loadMqttConfigs = async () => {
      try {
        const response = await axios.get('/api/mqtt-configs')
        mqttConfigs.value = Array.isArray(response.data) ? response.data : []
      } catch (error) {
        console.error('加载MQTT配置失败:', error)
        mqttConfigs.value = []
      }
    }

    // 加载主题配置列表
    const loadTopicConfigs = async () => {
      try {
        const response = await axios.get('/api/topic-configs')
        topicConfigs.value = Array.isArray(response.data) ? response.data : []
      } catch (error) {
        console.error('加载主题配置失败:', error)
        topicConfigs.value = []
      }
    }

    // 加载设备详情（编辑模式）
    const loadDevice = async () => {
      try {
        const response = await axios.get(`/api/devices/${route.params.id}`)
        const device = response.data
        deviceForm.value = {
          name: device.name,
          device_type: device.device_type,  // 映射到正确的字段
          location: device.location,
          clientid: device.clientid || '',  // EMQX 客户端 ID
          remark: device.remark || '',  // 备注字段
          show_on_dashboard: device.show_on_dashboard !== undefined ? device.show_on_dashboard : true,  // 是否在首页展示
          mqtt_config_id: device.mqtt_config_id || null,
          topic_config_id: device.topic_config_id || null,
          relay_on_payload: device.relay_on_payload || '',  // 继电器开启payload
          relay_off_payload: device.relay_off_payload || ''  // 继电器关闭payload
        }
      } catch (error) {
        console.error('加载设备详情失败:', error)
      }
    }

    // 保存设备
    const saveDevice = async () => {
      try {
        if (isEditing.value) {
          // 更新设备
          await axios.put(`/api/devices/${route.params.id}`, deviceForm.value)
          alert('设备更新成功')
        } else {
          // 添加设备
          await axios.post('/api/devices', deviceForm.value)
          alert('设备添加成功')
        }
        
        // 跳转回设备列表
        router.push('/devices')
      } catch (error) {
        console.error(isEditing.value ? '更新设备失败:' : '添加设备失败:', error)
        alert(isEditing.value ? '更新设备失败' : '添加设备失败')
      }
    }

    onMounted(async () => {
      await loadMqttConfigs()
      await loadTopicConfigs()
      
      if (isEditing.value) {
        await loadDevice()
      }
    })

    return {
      isEditing,
      deviceForm,
      mqttConfigs,
      topicConfigs,
      saveDevice
    }
  }
}
</script>