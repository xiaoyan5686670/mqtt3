<template>
  <div>
    <!-- 顶部横幅图片区域 -->
    <div class="header-banner mb-4">
      <div class="banner-container">
        <img src="/logo_center.png" alt="Logo" class="banner-image" />
        <div class="banner-overlay">
          <div class="banner-content">
            <h1 class="banner-title">设备仪表板</h1>
            <p class="banner-subtitle">MQTT IoT 管理系统</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 搜索框 -->
    <div class="search-container mb-4">
      <div class="search-box">
        <div class="search-input-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input
            type="text"
            class="search-input"
            placeholder="搜索设备名称、位置或类型..."
            v-model="searchKeyword"
            @input="handleSearch"
          />
          <button 
            v-if="searchKeyword"
            class="search-clear-btn" 
            type="button"
            @click="clearSearch"
            title="清除搜索"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div v-if="searchKeyword" class="search-result-info">
          <span class="search-count">
            找到 <strong>{{ filteredDevices.length }}</strong> 个设备
          </span>
        </div>
      </div>
    </div>

    <!-- 设备数据卡片网格 -->
    <div class="row">
      <div class="col-12">
        <div v-if="isLoading && filteredDevices.length === 0" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">加载中...</span>
          </div>
          <p class="mt-3 text-muted">正在加载设备数据...</p>
        </div>
        
        <div v-else-if="filteredDevices.length === 0 && !searchKeyword" class="text-center py-5">
          <div class="card">
            <div class="card-body">
              <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
              <p class="text-muted">暂无设备数据</p>
            </div>
          </div>
        </div>
        
        <div v-else-if="filteredDevices.length === 0 && searchKeyword" class="text-center py-5">
          <div class="card">
            <div class="card-body">
              <i class="fas fa-search fa-3x text-muted mb-3"></i>
              <p class="text-muted">未找到匹配的设备</p>
              <p class="text-muted small">请尝试其他关键词</p>
            </div>
          </div>
        </div>

        <div v-else class="row g-3">
          <div 
            v-for="deviceData in filteredDevices" 
            :key="deviceData.device.id"
            class="col-xl-3 col-lg-4 col-md-6 col-sm-12"
          >
            <div class="card h-100 shadow-sm device-card">
              <!-- 卡片头部：设备名称和状态 -->
              <div class="card-header py-2 px-3">
                <div class="d-flex justify-content-between align-items-start">
                  <div class="flex-grow-1">
                    <div class="d-flex align-items-center mb-1">
                      <h6 class="mb-0 me-2 device-name">
                        <i class="fas fa-microchip me-1"></i>
                        {{ deviceData.device.name }}
                      </h6>
                    </div>
                    <div class="d-flex flex-wrap gap-1 mb-1">
                      <!-- 设备类型标签 -->
                      <span 
                        v-if="deviceData.device.device_type"
                        class="badge bg-info"
                      >
                        {{ deviceData.device.device_type }}
                      </span>
                    </div>
                    <!-- 位置信息 -->
                    <small class="text-muted">
                      <i class="fas fa-map-marker-alt me-1"></i>
                      {{ deviceData.device.location || '未知位置' }}
                    </small>
                  </div>
                  <!-- 设备图标 -->
                  <div class="device-icon">
                    <i class="fas fa-server fa-2x text-primary"></i>
                  </div>
                </div>
              </div>
              
              <!-- 卡片主体：关键数据指标（温度、湿度优先） -->
              <div class="card-body py-2 px-3">
                <!-- 温度和湿度 - 重要指标，突出显示 -->
                <div v-if="hasPrioritySensors(deviceData.sensors)" class="priority-metrics mb-2">
                  <div class="row g-2">
                    <div 
                      v-for="sensor in getPrioritySensors(deviceData.sensors)" 
                      :key="sensor.id"
                      class="col-6"
                    >
                      <div class="metric-card">
                        <div class="metric-label">{{ getSensorDisplayName(sensor.type) }}</div>
                        <div class="metric-value">
                          {{ formatSensorValue(sensor.value) }}
                          <span class="metric-unit">{{ sensor.unit || '' }}</span>
                        </div>
                        <div class="metric-bar">
                          <div 
                            class="metric-progress" 
                            :class="getSensorStatusClass(sensor)"
                            :style="{ width: getSensorPercentage(sensor) + '%' }"
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 其他传感器数据 -->
                <div v-if="getOtherSensors(deviceData.sensors).length > 0" class="other-sensors">
                  <div 
                    v-for="sensor in getOtherSensors(deviceData.sensors)" 
                    :key="sensor.id"
                    class="sensor-row mb-1"
                  >
                    <div class="d-flex justify-content-between align-items-center">
                      <span class="sensor-label">{{ getSensorDisplayName(sensor.type) }}</span>
                      <div class="d-flex align-items-center">
                        <span class="sensor-value-small me-2">
                          {{ formatSensorValue(sensor.value) }}{{ sensor.unit || '' }}
                        </span>
                        <span 
                          v-if="sensor.type.includes('Relay') || sensor.type.includes('Level')"
                          class="badge badge-sm"
                          :class="sensor.value > 0 ? 'bg-success' : 'bg-secondary'"
                        >
                          {{ sensor.value > 0 ? 'ON' : 'OFF' }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 无数据提示 -->
                <div v-if="!deviceData.sensors || deviceData.sensors.length === 0" class="text-center text-muted py-2">
                  <small><i class="fas fa-exclamation-circle me-1"></i>暂无数据</small>
                </div>
              </div>
              
              <!-- 卡片底部：设备信息和操作 -->
              <div class="card-footer bg-transparent py-2 px-3">
                <div class="d-flex justify-content-between align-items-center">
                  <div class="device-info">
                    <small class="text-muted">
                      <span class="me-2">ID: {{ deviceData.device.id }}</span>
                      <span v-if="deviceData.device.created_at">
                        <i class="fas fa-calendar me-1"></i>
                        {{ formatShortDate(deviceData.device.created_at) }}
                      </span>
                    </small>
                  </div>
                  <div class="device-actions">
                    <router-link 
                      :to="`/devices/${deviceData.device.id}`" 
                      class="btn btn-sm btn-outline-primary"
                      title="查看详情"
                    >
                      <i class="fas fa-eye"></i>
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

export default {
  name: 'Dashboard',
  setup() {
    const devices = ref([])
    const devicesWithSensors = ref([])
    const filteredDevices = ref([])
    const isLoading = ref(false)
    const searchKeyword = ref('')
    let refreshInterval = null

    // 计算属性
    const onlineDevices = computed(() => devices.value.filter(d => d.status === '在线' || d.is_online).length)
    const offlineDevices = computed(() => devices.value.filter(d => d.status !== '在线' && !d.is_online).length)
    const sensorCount = computed(() => {
      return devicesWithSensors.value.reduce((count, deviceData) => {
        return count + (deviceData.sensors ? deviceData.sensors.length : 0)
      }, 0)
    })

    // 获取设备数据
    const fetchDevices = async () => {
      try {
        isLoading.value = true
        const response = await axios.get('/api/devices')
        devices.value = response.data
      } catch (error) {
        console.error('获取设备数据失败:', error)
      } finally {
        isLoading.value = false
      }
    }

    // 获取所有设备及其传感器数据
    const fetchDevicesWithSensors = async () => {
      try {
        await fetchDevices()
        
        const sensorsResponse = await axios.get('/api/sensors/latest')
        const allSensors = sensorsResponse.data || []
        
        const sensorMap = new Map()
        allSensors.forEach(sensor => {
          if (!sensorMap.has(sensor.device_id)) {
            sensorMap.set(sensor.device_id, [])
          }
          sensorMap.get(sensor.device_id).push(sensor)
        })
        
        devicesWithSensors.value = devices.value
          .filter(device => device.show_on_dashboard !== false)  // 只显示在首页展示的设备
          .map(device => {
            const sensors = sensorMap.get(device.id) || []
            const sensorTypeMap = new Map()
            sensors.forEach(sensor => {
              if (!sensorTypeMap.has(sensor.type) || 
                  new Date(sensor.timestamp) > new Date(sensorTypeMap.get(sensor.type).timestamp)) {
                sensorTypeMap.set(sensor.type, sensor)
              }
            })
            
            return {
              device,
              sensors: Array.from(sensorTypeMap.values()),
              isOnline: device.status === '在线' || device.is_online || false
            }
          })
        
        // 如果有搜索关键词，重新执行搜索过滤
        if (searchKeyword.value.trim()) {
          handleSearch()
        } else {
          filteredDevices.value = devicesWithSensors.value
        }
      } catch (error) {
        console.error('获取设备传感器数据失败:', error)
      }
    }

    // 处理搜索
    const handleSearch = () => {
      if (!searchKeyword.value.trim()) {
        filteredDevices.value = devicesWithSensors.value
        return
      }
      
      const keyword = searchKeyword.value.trim().toLowerCase()
      filteredDevices.value = devicesWithSensors.value.filter(deviceData => {
        const deviceName = (deviceData.device.name || '').toLowerCase()
        const deviceLocation = (deviceData.device.location || '').toLowerCase()
        const deviceType = (deviceData.device.device_type || '').toLowerCase()
        
        // 模糊匹配：设备名称、位置、类型
        return deviceName.includes(keyword) || 
               deviceLocation.includes(keyword) || 
               deviceType.includes(keyword)
      })
    }

    // 清除搜索
    const clearSearch = () => {
      searchKeyword.value = ''
      filteredDevices.value = devicesWithSensors.value
    }

    // 格式化传感器值
    const formatSensorValue = (value) => {
      if (typeof value === 'number') {
        return value.toFixed(1)
      }
      return value
    }

    // 判断是否为重要传感器（温度、湿度）
    const isPrioritySensor = (type) => {
      return type.includes('Temperature') || type.includes('Humidity')
    }

    // 获取重要传感器（温度、湿度）
    const getPrioritySensors = (sensors) => {
      return sensors.filter(s => isPrioritySensor(s.type)).sort((a, b) => {
        if (a.type.includes('Temperature') && b.type.includes('Humidity')) return -1
        if (a.type.includes('Humidity') && b.type.includes('Temperature')) return 1
        return a.type.localeCompare(b.type)
      })
    }

    // 获取其他传感器
    const getOtherSensors = (sensors) => {
      return sensors.filter(s => !isPrioritySensor(s.type))
    }

    // 检查是否有重要传感器
    const hasPrioritySensors = (sensors) => {
      return sensors && sensors.some(s => isPrioritySensor(s.type))
    }

    // 获取传感器显示名称
    const getSensorDisplayName = (type) => {
      const nameMap = {
        'Temperature1': '温度1',
        'Temperature2': '温度2',
        'Humidity1': '湿度1',
        'Humidity2': '湿度2',
        'Relay Status': '继电器',
        'PB8 Level': 'PB8'
      }
      return nameMap[type] || type
    }

    // 获取传感器百分比
    const getSensorPercentage = (sensor) => {
      if (sensor.min_value === null || sensor.max_value === null) {
        return 0
      }
      const percentage = ((sensor.value - sensor.min_value) / (sensor.max_value - sensor.min_value)) * 100
      return Math.min(100, Math.max(0, percentage))
    }

    // 获取传感器状态样式类
    const getSensorStatusClass = (sensor) => {
      if (sensor.type.includes('Temperature')) {
        if (sensor.value > 30) return 'bg-danger'
        if (sensor.value > 28) return 'bg-warning'
        return 'bg-success'
      } else if (sensor.type.includes('Humidity')) {
        if (sensor.value > 70) return 'bg-danger'
        if (sensor.value > 65) return 'bg-warning'
        return 'bg-success'
      }
      return 'bg-primary'
    }

    // 格式化日期时间
    const formatDate = (dateString) => {
      if (!dateString) return '未知'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // 格式化短日期
    const formatShortDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    }

    onMounted(async () => {
      await fetchDevicesWithSensors()
      
      refreshInterval = setInterval(async () => {
        await fetchDevicesWithSensors()
      }, 5000)
    })

    onUnmounted(() => {
      if (refreshInterval) {
        clearInterval(refreshInterval)
      }
    })

    return {
      devices,
      devicesWithSensors,
      filteredDevices,
      isLoading,
      searchKeyword,
      onlineDevices,
      offlineDevices,
      sensorCount,
      formatSensorValue,
      getSensorDisplayName,
      getSensorPercentage,
      getSensorStatusClass,
      formatDate,
      formatShortDate,
      getPrioritySensors,
      getOtherSensors,
      hasPrioritySensors,
      handleSearch,
      clearSearch
    }
  }
}
</script>

<style scoped>
.device-card {
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid #dee2e6;
}

.device-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.device-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: #212529;
}

.status-badge {
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  font-weight: 500;
}

.device-icon {
  opacity: 0.6;
}

/* 重要指标卡片样式 */
.priority-metrics {
  background: linear-gradient(135deg, #f0f7ff 0%, #ffffff 100%);
  border-radius: 6px;
  padding: 8px;
  border: 1px solid #e3f2fd;
}

.metric-card {
  background: white;
  border-radius: 4px;
  padding: 8px;
  border-left: 3px solid #2196F3;
}

.metric-label {
  font-size: 0.75rem;
  color: #6c757d;
  margin-bottom: 4px;
  font-weight: 500;
}

.metric-value {
  font-size: 1.3rem;
  font-weight: 700;
  color: #2196F3;
  line-height: 1.2;
}

.metric-unit {
  font-size: 0.8rem;
  color: #6c757d;
  font-weight: 400;
}

.metric-bar {
  height: 4px;
  background-color: #e9ecef;
  border-radius: 2px;
  margin-top: 6px;
  overflow: hidden;
}

.metric-progress {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

/* 其他传感器样式 */
.other-sensors {
  margin-top: 8px;
}

.sensor-row {
  padding: 4px 0;
  border-bottom: 1px solid #f0f0f0;
}

.sensor-row:last-child {
  border-bottom: none;
}

.sensor-label {
  font-size: 0.8rem;
  color: #6c757d;
}

.sensor-value-small {
  font-size: 0.85rem;
  font-weight: 600;
  color: #495057;
}

.badge-sm {
  font-size: 0.65rem;
  padding: 0.15rem 0.35rem;
}

/* 设备信息样式 */
.device-info {
  font-size: 0.75rem;
}

.device-actions .btn {
  padding: 0.2rem 0.5rem;
  font-size: 0.8rem;
}

/* 搜索框样式 */
.search-container {
  margin: 0 -15px 20px -15px;
  padding: 0 15px;
}

.search-box {
  max-width: 600px;
  margin: 0 auto;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: #ffffff;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 0 16px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.search-input-wrapper:focus-within {
  border-color: #007bff;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
}

.search-icon {
  color: #6c757d;
  font-size: 1rem;
  margin-right: 12px;
  flex-shrink: 0;
}

.search-input-wrapper:focus-within .search-icon {
  color: #007bff;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 12px 8px;
  font-size: 1rem;
  background: transparent;
  color: #212529;
}

.search-input::placeholder {
  color: #adb5bd;
}

.search-clear-btn {
  background: transparent;
  border: none;
  color: #6c757d;
  padding: 4px 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  transition: all 0.2s ease;
  flex-shrink: 0;
  margin-left: 8px;
}

.search-clear-btn:hover {
  background: #f8f9fa;
  color: #495057;
}

.search-result-info {
  margin-top: 12px;
  text-align: center;
}

.search-count {
  color: #6c757d;
  font-size: 0.875rem;
}

.search-count strong {
  color: #007bff;
  font-weight: 600;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .metric-value {
    font-size: 1.1rem;
  }
  
  .device-name {
    font-size: 0.85rem;
  }
  
  .search-box {
    max-width: 100%;
  }
  
  .search-input-wrapper {
    padding: 0 12px;
  }
  
  .search-input {
    padding: 10px 6px;
    font-size: 0.95rem;
  }
}

@media (max-width: 576px) {
  .search-input {
    font-size: 0.9rem;
  }
  
  .search-icon {
    font-size: 0.9rem;
    margin-right: 8px;
  }
}

/* 顶部横幅样式 */
.header-banner {
  margin: -15px -15px 30px -15px;
  border-radius: 0;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.banner-container {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.banner-image {
  max-width: 100%;
  max-height: 100%;
  height: auto;
  width: auto;
  object-fit: contain;
  display: block;
  transition: transform 0.5s ease;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.banner-container:hover .banner-image {
  transform: scale(1.05);
}

.banner-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.3) 0%,
    rgba(0, 0, 0, 0.1) 50%,
    rgba(0, 0, 0, 0.4) 100%
  );
  display: flex;
  align-items: center;
  justify-content: center;
}

.banner-content {
  text-align: center;
  color: white;
  padding: 20px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.banner-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 10px;
  letter-spacing: 2px;
}

.banner-subtitle {
  font-size: 1.2rem;
  font-weight: 300;
  opacity: 0.95;
  letter-spacing: 1px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .banner-container {
    height: 200px;
  }
  
  .banner-title {
    font-size: 1.8rem;
  }
  
  .banner-subtitle {
    font-size: 1rem;
  }
}

@media (max-width: 576px) {
  .banner-container {
    height: 160px;
  }
  
  .banner-title {
    font-size: 1.5rem;
    margin-bottom: 5px;
  }
  
  .banner-subtitle {
    font-size: 0.9rem;
  }
}

/* 标题区域样式（当没有图片时） */
.header-title-section {
  padding: 30px 0;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-bottom: 2px solid #e9ecef;
  margin: -15px -15px 20px -15px;
}

.header-title-section h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #212529;
}

.header-title-section p {
  font-size: 1rem;
  margin-bottom: 0;
}
</style>
