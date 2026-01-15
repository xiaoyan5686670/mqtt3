<template>
  <div class="real-time-data">
    <div class="container-fluid py-4">
      <!-- 头部控制栏 -->
      <div class="header-panel card shadow-sm mb-4">
        <div class="card-body p-4">
          <div class="row align-items-center">
            <div class="col-lg-4 col-md-12 mb-3 mb-lg-0">
              <h2 class="page-title d-flex align-items-center">
                <div class="title-icon me-3">
                  <i class="fas fa-chart-line text-white"></i>
                </div>
                <span>实时监控中心</span>
              </h2>
            </div>
            <div class="col-lg-5 col-md-8 mb-3 mb-md-0">
              <div class="device-select-wrapper">
                <div class="input-group">
                  <span class="input-group-text bg-white border-end-0">
                    <i class="fas fa-microchip text-primary"></i>
                  </span>
                  <select 
                    class="form-select border-start-0 ps-0" 
                    v-model="selectedDeviceId"
                    @change="onDeviceChange"
                  >
                    <option value="">请选择监控设备...</option>
                    <option v-for="device in devices" :key="device.id" :value="device.id">
                      {{ device.name }} ({{ device.location || '默认位置' }})
                    </option>
                  </select>
                  <button 
                    class="btn btn-primary px-4"
                    :disabled="!selectedDeviceId"
                    @click="refreshData"
                  >
                    <i class="fas fa-sync-alt me-1"></i> 刷新
                  </button>
                </div>
              </div>
            </div>
            <div class="col-lg-3 col-md-4 text-end">
              <div class="status-badge" :class="{ 'active': selectedDeviceId }">
                <span class="pulse-dot"></span>
                {{ selectedDeviceId ? '设备在线' : '等待选择' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="selectedDeviceId">
        <!-- 维度切换器 -->
        <div class="time-range-wrapper mb-4 text-center">
          <div class="btn-group shadow-sm p-1 bg-white rounded-pill d-inline-flex">
            <button 
              v-for="range in ['realtime', 'day', 'week', 'month']" 
              :key="range"
              type="button" 
              class="btn rounded-pill px-4 py-2 border-0"
              :class="timeRange === range ? 'btn-primary shadow-sm' : 'btn-light text-muted'"
              @click="setTimeRange(range)"
            >
              <i :class="getRangeIcon(range)" class="me-2"></i>
              {{ getRangeText(range) }}
            </button>
          </div>
        </div>

        <!-- 传感器卡片网格 -->
        <div v-if="!loadingData" class="row g-4 mb-5">
          <div class="col-xl-4 col-md-6">
            <div class="sensor-glass-card temperature">
              <div class="card-overlay"></div>
              <div class="card-content">
                <div class="sensor-header mb-4">
                  <span class="sensor-label">温度监测</span>
                  <div class="sensor-icon-circle">
                    <i class="fas fa-temperature-high"></i>
                  </div>
                </div>
                <div class="sensor-values">
                  <div class="value-item main">
                    <span class="number">{{ sensorData.temp1 }}</span>
                    <span class="unit">°C</span>
                    <span class="sub-label">主传感器</span>
                  </div>
                  <div class="value-divider"></div>
                  <div class="value-item secondary">
                    <span class="number">{{ sensorData.temp2 }}</span>
                    <span class="unit">°C</span>
                    <span class="sub-label">备用传感器</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="col-xl-4 col-md-6">
            <div class="sensor-glass-card humidity">
              <div class="card-overlay"></div>
              <div class="card-content">
                <div class="sensor-header mb-4">
                  <span class="sensor-label">湿度监测</span>
                  <div class="sensor-icon-circle">
                    <i class="fas fa-tint"></i>
                  </div>
                </div>
                <div class="sensor-values">
                  <div class="value-item main">
                    <span class="number">{{ sensorData.hum1 }}</span>
                    <span class="unit">%</span>
                    <span class="sub-label">环境湿度</span>
                  </div>
                  <div class="value-divider"></div>
                  <div class="value-item secondary">
                    <span class="number">{{ sensorData.hum2 }}</span>
                    <span class="unit">%</span>
                    <span class="sub-label">基准湿度</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="col-xl-4 col-md-12">
            <div class="sensor-glass-card control">
              <div class="card-overlay"></div>
              <div class="card-content">
                <div class="sensor-header mb-4">
                  <span class="sensor-label">系统控制</span>
                  <div class="sensor-icon-circle">
                    <i class="fas fa-cogs"></i>
                  </div>
                </div>
                <div class="control-items">
                  <div class="control-row mb-3">
                    <div class="control-info">
                      <i class="fas fa-plug me-2" :class="sensorData.relay === 1 ? 'text-warning' : 'text-white-50'"></i>
                      <span>继电器状态</span>
                    </div>
                    <button 
                      class="control-btn" 
                      :class="{ 'active': sensorData.relay === 1, 'loading': sendingRelay }"
                      @click="toggleRelay"
                      :disabled="sendingRelay"
                    >
                      <div v-if="sendingRelay" class="spinner-border spinner-border-sm"></div>
                      <span v-else>{{ sensorData.relay === 1 ? 'ON' : 'OFF' }}</span>
                    </button>
                  </div>
                  <div class="control-row">
                    <div class="control-info">
                      <i class="fas fa-bolt me-2" :class="sensorData.pb8 === 1 ? 'text-warning' : 'text-white-50'"></i>
                      <span>PB8 逻辑电平</span>
                    </div>
                    <div class="status-pill" :class="sensorData.pb8 === 1 ? 'high' : 'low'">
                      {{ sensorData.pb8 === 1 ? 'HIGH' : 'LOW' }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 图表展示区域 -->
        <div v-if="!loadingData" class="trend-section">
          <div class="section-header mb-4 d-flex align-items-center justify-content-between">
            <div>
              <h4 class="section-title mb-0">趋势数据分析</h4>
              <div class="section-line"></div>
            </div>
            <div v-if="timeRange === 'month'" class="custom-date-picker d-flex align-items-center bg-white px-3 py-2 rounded-pill shadow-sm">
              <div class="picker-label me-3 d-none d-md-flex align-items-center">
                <i class="fas fa-calendar-alt text-primary me-2"></i>
                <span class="text-muted small fw-600">自定义日期区间</span>
              </div>
              <div class="d-flex align-items-center">
                <input 
                  type="date" 
                  v-model="startDate" 
                  class="date-input" 
                  @change="refreshData"
                >
                <span class="mx-2 text-muted">至</span>
                <input 
                  type="date" 
                  v-model="endDate" 
                  class="date-input" 
                  @change="refreshData"
                >
              </div>
            </div>
          </div>
          <div class="row g-4">
            <div class="col-lg-6">
              <div class="chart-box card border-0 shadow-sm">
                <div class="card-body p-4">
                  <div ref="chart1Ref" class="chart-element"></div>
                </div>
              </div>
            </div>
            <div class="col-lg-6">
              <div class="chart-box card border-0 shadow-sm">
                <div class="card-body p-4">
                  <div ref="chart2Ref" class="chart-element"></div>
                </div>
              </div>
            </div>
            <div v-if="timeRange === 'realtime'" class="col-12">
              <div class="chart-box card border-0 shadow-sm">
                <div class="card-body p-4">
                  <div ref="chart3Ref" class="chart-element full-width"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loadingData" class="loading-state py-5 text-center">
          <div class="loader-wave">
            <span></span><span></span><span></span><span></span>
          </div>
          <p class="mt-4 text-muted fw-500">同步设备数据中...</p>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!selectedDeviceId && !loadingData" class="empty-state-card text-center py-5 shadow-sm bg-white rounded-4">
        <div class="empty-illustration mb-4">
          <div class="icon-circle shadow-sm mx-auto">
            <i class="fas fa-broadcast-tower fa-3x text-primary"></i>
          </div>
        </div>
        <h3 class="mb-3">等待设备连接</h3>
        <p class="text-muted mb-4 mx-auto" style="max-width: 400px;">
          请从顶部面板选择一个已注册的物联网设备，系统将自动建立实时数据通道并为您展示多维度的监控图表。
        </p>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-toast">
        <i class="fas fa-exclamation-circle me-2"></i>
        {{ error }}
        <button class="btn-close btn-close-white ms-3" @click="error = ''"></button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

export default {
  name: 'RealTimeData',
  setup() {
    // 传感器数据
    const sensorData = ref({
      temp1: 0,
      hum1: 0,
      temp2: 0,
      hum2: 0,
      relay: 0,
      pb8: 0
    })
    
    // 设备列表
    const devices = ref([])
    
    // 当前选中的设备ID
    const selectedDeviceId = ref('')
    
    // 加载状态
    const loadingData = ref(false)
    
    // 错误信息
    const error = ref('')
    
    // 继电器控制状态
    const sendingRelay = ref(false)
    
    // 继电器期望状态和最后操作时间（用于乐观更新，避免轮询覆盖）
    const relayExpectedState = ref({
      value: null,  // 期望的状态值（0或1），null表示没有待确认的状态
      timestamp: 0,  // 最后操作的时间戳
      timeout: 5000  // 超时时间（5秒），超过这个时间后不再保护
    })
    
    // 时间范围：realtime / day / week / month
    const timeRange = ref('realtime')

    // 自定义日期区间（用于月维度）
    const getInitialDateRange = () => {
      const now = new Date()
      const firstDay = new Date(now.getFullYear(), now.getMonth(), 1)
      const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0)
      
      const format = (date) => {
        const y = date.getFullYear()
        const m = String(date.getMonth() + 1).padStart(2, '0')
        const d = String(date.getDate()).padStart(2, '0')
        return `${y}-${m}-${d}`
      }
      
      return {
        start: format(firstDay),
        end: format(lastDay)
      }
    }

    const initialRange = getInitialDateRange()
    const startDate = ref(initialRange.start)
    const endDate = ref(initialRange.end)

    // 获取时间范围对应的图标
    const getRangeIcon = (range) => {
      const icons = {
        realtime: 'fas fa-bolt',
        day: 'fas fa-calendar-day',
        week: 'fas fa-calendar-week',
        month: 'fas fa-calendar-alt'
      }
      return icons[range]
    }

    // 获取时间范围对应的文字
    const getRangeText = (range) => {
      const texts = {
        realtime: '实时',
        day: '日维度',
        week: '周趋势',
        month: '月分析'
      }
      return texts[range]
    }

    // 获取指定设备的发布主题（用于继电器控制等）
    const fetchPublishTopic = async (deviceId) => {
      try {
        const resp = await axios.get(`/api/devices/${deviceId}/publish-topic`)
        const topic = resp?.data?.publish_topic
        if (topic && typeof topic === 'string' && topic.trim()) {
          return topic.trim()
        }
      } catch (e) {
        console.warn('获取设备发布主题失败，使用按设备隔离的默认主题:', e)
      }
      return `pc/${deviceId}`
    }
    
    // 图表引用
    const chart1Ref = ref(null)
    const chart2Ref = ref(null)
    const chart3Ref = ref(null)
    
    // 图表实例
    let chart1 = null
    let chart2 = null
    let chart3 = null
    
    // 图表数据
    const chartData = ref({
      timeStamps: [],
      temp1Data: [],
      hum1Data: [],
      temp2Data: [],
      hum2Data: [],
      relayData: [],
      pb8Data: []
    })
    
    // 获取设备列表
    const fetchDevices = async () => {
      try {
        const response = await axios.get('/api/devices')
        devices.value = response.data
      } catch (error) {
        console.error('获取设备列表失败:', error)
        error.value = '获取设备列表失败: ' + error.message
      }
    }
    
    // 更新图表（实时模式）
    const updateChartsRealtime = () => {
      const now = new Date().toLocaleTimeString()
      
      chartData.value.timeStamps.push(now)
      if(chartData.value.timeStamps.length > 20) {
        chartData.value.timeStamps.shift()
      }
      
      chartData.value.temp1Data.push(sensorData.value.temp1)
      chartData.value.hum1Data.push(sensorData.value.hum1)
      chartData.value.temp2Data.push(sensorData.value.temp2)
      chartData.value.hum2Data.push(sensorData.value.hum2)
      chartData.value.relayData.push(sensorData.value.relay)
      chartData.value.pb8Data.push(sensorData.value.pb8)
      
      if(chartData.value.temp1Data.length > 20) chartData.value.temp1Data.shift()
      if(chartData.value.hum1Data.length > 20) chartData.value.hum1Data.shift()
      if(chartData.value.temp2Data.length > 20) chartData.value.temp2Data.shift()
      if(chartData.value.hum2Data.length > 20) chartData.value.hum2Data.shift()
      if(chartData.value.relayData.length > 20) chartData.value.relayData.shift()
      if(chartData.value.pb8Data.length > 20) chartData.value.pb8Data.shift()
      
      renderCharts()
    }
    
    // 渲染图表
    const renderCharts = () => {
      nextTick(() => {
        // 图表1 - 温度趋势
        if (chart1Ref.value) {
          if (chart1) { chart1.dispose(); chart1 = null; }
          chart1 = echarts.init(chart1Ref.value)
          
          const option1 = {
            title: {
              text: '温度趋势 (℃)',
              left: 'left',
              textStyle: { fontSize: 16, fontWeight: 'bold', color: '#333' }
            },
            tooltip: {
              trigger: 'axis',
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              borderWidth: 1,
              borderColor: '#eee',
              padding: [10, 15],
              axisPointer: { type: 'line', lineStyle: { color: '#aaa', type: 'dashed' } }
            },
            legend: { data: ['温度1', '温度2'], top: 0, right: 0, icon: 'circle' },
            grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
            xAxis: {
              type: 'category',
              boundaryGap: timeRange.value !== 'day',
              data: chartData.value.timeStamps,
              axisLine: { lineStyle: { color: '#eee' } },
              axisLabel: { color: '#999', rotate: timeRange.value === 'day' ? 0 : 30 }
            },
            yAxis: {
              type: 'value',
              splitLine: { lineStyle: { type: 'dashed', color: '#f5f5f5' } },
              axisLine: { show: false },
              scale: true
            },
            series: [
              {
                name: '温度1',
                type: 'line',
                data: chartData.value.temp1Data,
                itemStyle: { color: '#FF6384' },
                lineStyle: { width: 3 },
                smooth: true,
                showSymbol: true,
                symbolSize: 8,
                areaStyle: {
                  color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(255, 99, 132, 0.2)' },
                    { offset: 1, color: 'rgba(255, 99, 132, 0)' }
                  ])
                }
              },
              {
                name: '温度2',
                type: 'line',
                data: chartData.value.temp2Data,
                itemStyle: { color: '#36A2EB' },
                lineStyle: { width: 3 },
                smooth: true,
                showSymbol: true,
                symbolSize: 8,
                areaStyle: {
                  color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(54, 162, 235, 0.2)' },
                    { offset: 1, color: 'rgba(54, 162, 235, 0)' }
                  ])
                }
              }
            ]
          }
          chart1.setOption(option1, { notMerge: true })
        }
        
        // 图表2 - 湿度趋势
        if (chart2Ref.value) {
          if (chart2) { chart2.dispose(); chart2 = null; }
          chart2 = echarts.init(chart2Ref.value)
          
          const option2 = {
            title: {
              text: '湿度趋势 (%)',
              left: 'left',
              textStyle: { fontSize: 16, fontWeight: 'bold', color: '#333' }
            },
            tooltip: {
              trigger: 'axis',
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              borderWidth: 1,
              borderColor: '#eee',
              padding: [10, 15],
              axisPointer: { type: 'line', lineStyle: { color: '#aaa', type: 'dashed' } }
            },
            legend: { data: ['湿度1', '湿度2'], top: 0, right: 0, icon: 'circle' },
            grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
            xAxis: {
              type: 'category',
              boundaryGap: timeRange.value !== 'day',
              data: chartData.value.timeStamps,
              axisLine: { lineStyle: { color: '#eee' } },
              axisLabel: { color: '#999', rotate: timeRange.value === 'day' ? 0 : 30 }
            },
            yAxis: {
              type: 'value',
              splitLine: { lineStyle: { type: 'dashed', color: '#f5f5f5' } },
              axisLine: { show: false },
              scale: true
            },
            series: [
              {
                name: '湿度1',
                type: 'line',
                data: chartData.value.hum1Data,
                itemStyle: { color: '#4CAF50' },
                lineStyle: { width: 3 },
                smooth: true,
                showSymbol: true,
                symbolSize: 8,
                areaStyle: {
                  color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(76, 175, 80, 0.2)' },
                    { offset: 1, color: 'rgba(76, 175, 80, 0)' }
                  ])
                }
              },
              {
                name: '湿度2',
                type: 'line',
                data: chartData.value.hum2Data,
                itemStyle: { color: '#2196F3' },
                lineStyle: { width: 3 },
                smooth: true,
                showSymbol: true,
                symbolSize: 8,
                areaStyle: {
                  color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(33, 150, 243, 0.2)' },
                    { offset: 1, color: 'rgba(33, 150, 243, 0)' }
                  ])
                }
              }
            ]
          }
          chart2.setOption(option2, { notMerge: true })
        }
        
        // 图表3 - 继电器和PB8
        if (timeRange.value === 'realtime' && chart3Ref.value) {
          if (!chart3) chart3 = echarts.init(chart3Ref.value)
          const option3 = {
            title: {
              text: '控制状态趋势',
              left: 'left',
              textStyle: { fontSize: 16, fontWeight: 'bold', color: '#333' }
            },
            tooltip: { trigger: 'axis' },
            legend: { data: ['继电器', 'PB8'], top: 0, right: 0, icon: 'rect' },
            grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
            xAxis: {
              type: 'category',
              boundaryGap: false,
              data: chartData.value.timeStamps,
              axisLine: { lineStyle: { color: '#eee' } }
            },
            yAxis: {
              type: 'value',
              min: 0, max: 1, interval: 1,
              axisLabel: { formatter: (v) => v === 1 ? 'ON/高' : 'OFF/低' },
              splitLine: { lineStyle: { type: 'dashed', color: '#f5f5f5' } }
            },
            series: [
              {
                name: '继电器',
                type: 'line',
                step: 'start',
                data: chartData.value.relayData,
                itemStyle: { color: '#4CAF50' },
                areaStyle: { color: 'rgba(76, 175, 80, 0.05)' }
              },
              {
                name: 'PB8',
                type: 'line',
                step: 'start',
                data: chartData.value.pb8Data,
                itemStyle: { color: '#2196F3' },
                areaStyle: { color: 'rgba(33, 150, 243, 0.05)' }
              }
            ]
          }
          chart3.setOption(option3, { notMerge: true })
        }
      })
    }
    
    // 获取实时数据
    const fetchRealTimeData = async () => {
      if (!selectedDeviceId.value) return
      
      if (chartData.value.timeStamps.length === 0) loadingData.value = true
      error.value = ''
      
      try {
        const response = await axios.get(`/api/devices/${selectedDeviceId.value}/latest-sensors`)
        const sensors = response.data
        const tempSensorData = { ...sensorData.value }
        
        // 重置
        tempSensorData.temp1 = 0; tempSensorData.hum1 = 0;
        tempSensorData.temp2 = 0; tempSensorData.hum2 = 0;
        tempSensorData.relay = 0; tempSensorData.pb8 = 0;
        
        for (const sensor of sensors) {
          if (sensor.type === 'Temperature1') tempSensorData.temp1 = sensor.value
          else if (sensor.type === 'Humidity1') tempSensorData.hum1 = sensor.value
          else if (sensor.type === 'Temperature2') tempSensorData.temp2 = sensor.value
          else if (sensor.type === 'Humidity2') tempSensorData.hum2 = sensor.value
          else if (sensor.type === 'Relay Status') {
            const now = Date.now()
            const timeSinceOperation = now - relayExpectedState.value.timestamp
            if (relayExpectedState.value.value !== null && timeSinceOperation < relayExpectedState.value.timeout) {
              tempSensorData.relay = sensor.value === relayExpectedState.value.value ? sensor.value : relayExpectedState.value.value
              if (sensor.value === relayExpectedState.value.value) relayExpectedState.value.value = null
            } else {
              relayExpectedState.value.value = null
              tempSensorData.relay = sensor.value
            }
          } else if (sensor.type === 'PB8 Level') tempSensorData.pb8 = sensor.value
        }
        
        sensorData.value = tempSensorData
        if (timeRange.value === 'realtime') updateChartsRealtime()
      } catch (err) {
        console.error('获取实时数据失败:', err)
        error.value = `获取数据失败: ${err.message}`
      } finally {
        loadingData.value = false
      }
    }
    
    // 加载历史数据
    const loadHistoryData = async () => {
      if (!selectedDeviceId.value) return
      loadingData.value = true
      error.value = ''

      try {
        const params = {
          limit: timeRange.value === 'month' ? 2000 : 1000
        }

        if (timeRange.value === 'month') {
          params.start_time = `${startDate.value}T00:00:00`
          params.end_time = `${endDate.value}T23:59:59`
        } else {
          params.time_range = timeRange.value
        }

        const response = await axios.get(`/api/sensors/device/${selectedDeviceId.value}/history`, {
          params
        })

        const sensors = response.data || []
        if (sensors.length === 0) {
          chartData.value = { timeStamps: [], temp1Data: [], hum1Data: [], temp2Data: [], hum2Data: [], relayData: [], pb8Data: [] }
          loadingData.value = false
          renderCharts()
          return
        }

        const dataMap = { Temperature1: [], Temperature2: [], Humidity1: [], Humidity2: [] }
        sensors.forEach(item => {
          if (dataMap[item.type]) {
            let tsStr = item.timestamp
            if (!tsStr.endsWith('Z') && !tsStr.includes('+')) tsStr += 'Z'
            const timestamp = new Date(tsStr)
            dataMap[item.type].push({ timestamp: timestamp.getTime(), value: parseFloat(item.value) })
          }
        })

        const allTimestamps = new Set()
        Object.values(dataMap).forEach(arr => arr.forEach(item => allTimestamps.add(item.timestamp)))
        const sortedTimestamps = Array.from(allTimestamps).sort((a, b) => a - b)
        
        const createMap = (arr) => {
          const m = new Map()
          arr.forEach(item => m.set(item.timestamp, item.value))
          return m
        }
        const temp1Map = createMap(dataMap.Temperature1)
        const temp2Map = createMap(dataMap.Temperature2)
        const hum1Map = createMap(dataMap.Humidity1)
        const hum2Map = createMap(dataMap.Humidity2)

        let timeLabels = []; let temp1Data = []; let temp2Data = []; let hum1Data = []; let hum2Data = [];

        if (timeRange.value === 'day') {
          // 日维度：固定 0-23 小时 X 轴，每小时一个汇总点
          timeLabels = Array.from({ length: 24 }, (_, i) => `${i}`)
          const buckets = Array.from({ length: 24 }, () => ({ t1: [], t2: [], h1: [], h2: [] }))
          sortedTimestamps.forEach(ts => {
            const h = new Date(ts).getHours()
            if (temp1Map.has(ts)) buckets[h].t1.push(temp1Map.get(ts))
            if (temp2Map.has(ts)) buckets[h].t2.push(temp2Map.get(ts))
            if (hum1Map.has(ts)) buckets[h].h1.push(hum1Map.get(ts))
            if (hum2Map.has(ts)) buckets[h].h2.push(hum2Map.get(ts))
          })
          const avg = (arr) => arr.length ? parseFloat((arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1)) : null
          temp1Data = buckets.map(b => avg(b.t1)); temp2Data = buckets.map(b => avg(b.t2));
          hum1Data = buckets.map(b => avg(b.h1)); hum2Data = buckets.map(b => avg(b.h2));
        } else if (timeRange.value === 'week') {
          // 周维度：自然周区间（周一至周日），以天为单位
          const weekDays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
          timeLabels = weekDays
          
          // 初始化 7 天的数据桶
          const buckets = Array.from({ length: 7 }, () => ({ t1: [], t2: [], h1: [], h2: [] }))
          
          sortedTimestamps.forEach(ts => {
            const date = new Date(ts)
            let dayIdx = date.getDay() // 0(周日) - 6(周六)
            // 转换为周一为起始的索引：周一(0) - 周日(6)
            const mappedIdx = dayIdx === 0 ? 6 : dayIdx - 1
            
            if (temp1Map.has(ts)) buckets[mappedIdx].t1.push(temp1Map.get(ts))
            if (temp2Map.has(ts)) buckets[mappedIdx].t2.push(temp2Map.get(ts))
            if (hum1Map.has(ts)) buckets[mappedIdx].h1.push(hum1Map.get(ts))
            if (hum2Map.has(ts)) buckets[mappedIdx].h2.push(hum2Map.get(ts))
          })
          
          const avg = (arr) => arr.length ? parseFloat((arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1)) : null
          temp1Data = buckets.map(b => avg(b.t1))
          temp2Data = buckets.map(b => avg(b.t2))
          hum1Data = buckets.map(b => avg(b.h1))
          hum2Data = buckets.map(b => avg(b.h2))
        } else {
          // 月维度：按天聚合，显示范围内每一天，处理自然月及平/闰年
          const start = new Date(startDate.value)
          const end = new Date(endDate.value)
          
          let current = new Date(start)
          const dayBuckets = []
          while (current <= end) {
            dayBuckets.push({
              date: new Date(current),
              label: `${current.getMonth() + 1}月${current.getDate()}日`,
              t1: [], t2: [], h1: [], h2: []
            })
            // 使用 setDate(+1) 自动处理跨月、跨年、平闰年逻辑
            current.setDate(current.getDate() + 1)
          }

          sortedTimestamps.forEach(ts => {
            const d = new Date(ts)
            // 找到对应的日期桶（忽略时分秒）
            const bucket = dayBuckets.find(b => 
              b.date.getFullYear() === d.getFullYear() &&
              b.date.getMonth() === d.getMonth() &&
              b.date.getDate() === d.getDate()
            )
            if (bucket) {
              if (temp1Map.has(ts)) bucket.t1.push(temp1Map.get(ts))
              if (temp2Map.has(ts)) bucket.t2.push(temp2Map.get(ts))
              if (hum1Map.has(ts)) bucket.h1.push(hum1Map.get(ts))
              if (hum2Map.has(ts)) bucket.h2.push(hum2Map.get(ts))
            }
          })

          const avg = (arr) => arr.length ? parseFloat((arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1)) : null
          
          timeLabels = dayBuckets.map(b => b.label)
          temp1Data = dayBuckets.map(b => avg(b.t1))
          temp2Data = dayBuckets.map(b => avg(b.t2))
          hum1Data = dayBuckets.map(b => avg(b.h1))
          hum2Data = dayBuckets.map(b => avg(b.h2))
        }
        
        chartData.value = { timeStamps: timeLabels, temp1Data, temp2Data, hum1Data, hum2Data, relayData: [], pb8Data: [] }
        loadingData.value = false
        await nextTick(); renderCharts()
      } catch (err) {
        console.error('加载历史数据失败:', err)
        error.value = `加载历史数据失败: ${err.message}`
      } finally {
        loadingData.value = false
      }
    }

    const onDeviceChange = () => {
      localStorage.setItem('selectedDeviceId', selectedDeviceId.value)
      chartData.value = { timeStamps: [], temp1Data: [], hum1Data: [], temp2Data: [], hum2Data: [], relayData: [], pb8Data: [] }
      if (timeRange.value === 'realtime') fetchRealTimeData()
      else loadHistoryData()
    }
    
    const setTimeRange = (range) => {
      if (timeRange.value === range) return
      timeRange.value = range
      chartData.value = { timeStamps: [], temp1Data: [], hum1Data: [], temp2Data: [], hum2Data: [], relayData: [], pb8Data: [] }
      if (range === 'realtime') fetchRealTimeData()
      else loadHistoryData()
    }
    
    const refreshData = () => {
      if (timeRange.value === 'realtime') fetchRealTimeData()
      else loadHistoryData()
    }
    
    const handleResize = () => {
      if (chart1) chart1.resize()
      if (chart2) chart2.resize()
      if (chart3) chart3.resize()
    }
    
    onMounted(async () => {
      await fetchDevices()
      const saved = localStorage.getItem('selectedDeviceId')
      if (saved && devices.value.some(d => d.id == saved)) selectedDeviceId.value = saved
      if (selectedDeviceId.value) fetchRealTimeData()
      window.addEventListener('resize', handleResize)
      window.realtimeInterval = setInterval(() => {
        if (selectedDeviceId.value && timeRange.value === 'realtime') fetchRealTimeData()
      }, 3000)
    })
    
    onUnmounted(() => {
      if (window.realtimeInterval) clearInterval(window.realtimeInterval)
      window.removeEventListener('resize', handleResize)
      if (chart1) chart1.dispose()
      if (chart2) chart2.dispose()
      if (chart3) chart3.dispose()
    })
    
    const toggleRelay = async () => {
      if (!selectedDeviceId.value) return
      sendingRelay.value = true
      try {
        const topic = await fetchPublishTopic(selectedDeviceId.value)
        const isCurrentlyOn = sensorData.value.relay === 1
        const message = isCurrentlyOn ? 'relayoff' : 'relayon'
        const response = await axios.post('/api/mqtt/publish', { topic, message, qos: 0 })
        if (response.data.success) {
          const newState = isCurrentlyOn ? 0 : 1
          sensorData.value.relay = newState
          relayExpectedState.value = { value: newState, timestamp: Date.now(), timeout: 5000 }
        }
      } catch (err) {
        error.value = `控制失败: ${err.message}`
      } finally {
        sendingRelay.value = false
      }
    }
    
    return {
      sensorData, devices, selectedDeviceId, loadingData, error, sendingRelay,
      onDeviceChange, chart1Ref, chart2Ref, chart3Ref, refreshData, toggleRelay,
      timeRange, setTimeRange, getRangeIcon, getRangeText,
      startDate, endDate
    }
  }
}
</script>

<style scoped>
.real-time-data {
  min-height: 100vh;
  background-color: #f0f2f5;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* 头部面板 */
.header-panel {
  border: none;
  border-radius: 1.25rem;
  background: white;
}

.title-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.3);
}

.page-title span {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1a1a;
  letter-spacing: -0.5px;
}

/* 设备选择 */
.device-select-wrapper .input-group {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}

.device-select-wrapper .form-select {
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border-color: #eee;
  background-color: #fff;
}

.device-select-wrapper .form-select:focus {
  box-shadow: none;
  border-color: #4facfe;
}

/* 状态标签 */
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1.25rem;
  background: #f8f9fa;
  border-radius: 100px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #6c757d;
  transition: all 0.3s ease;
}

.status-badge.active {
  background: rgba(40, 167, 69, 0.1);
  color: #28a745;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background-color: currentColor;
  border-radius: 50%;
  margin-right: 10px;
  position: relative;
}

.active .pulse-dot::after {
  content: '';
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background-color: currentColor;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.8; }
  100% { transform: scale(3); opacity: 0; }
}

/* 传感器玻璃卡片 */
.sensor-glass-card {
  position: relative;
  padding: 2rem;
  border-radius: 2rem;
  overflow: hidden;
  color: white;
  min-height: 220px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.sensor-glass-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0,0,0,0.15);
}

.sensor-glass-card.temperature { background: linear-gradient(135deg, #ff6b6b 0%, #f06595 100%); }
.sensor-glass-card.humidity { background: linear-gradient(135deg, #37b24d 0%, #2f9e44 100%); }
.sensor-glass-card.control { background: linear-gradient(135deg, #1c7ed6 0%, #1971c2 100%); }

.card-overlay {
  position: absolute;
  top: -20%; right: -10%;
  width: 200px; height: 200px;
  background: rgba(255,255,255,0.1);
  border-radius: 50%;
}

.card-content { position: relative; z-index: 1; }

.sensor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sensor-label { font-size: 1.1rem; font-weight: 600; opacity: 0.9; }

.sensor-icon-circle {
  width: 44px; height: 44px;
  background: rgba(255,255,255,0.2);
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem;
}

.sensor-values { display: flex; align-items: center; justify-content: space-around; }

.value-item { display: flex; flex-direction: column; align-items: center; }

.value-item .number { font-size: 2.5rem; font-weight: 800; line-height: 1; }
.value-item .unit { font-size: 1.1rem; font-weight: 600; opacity: 0.8; margin-bottom: 4px; }
.value-item .sub-label { font-size: 0.75rem; opacity: 0.7; font-weight: 500; }

.value-divider { width: 1px; height: 40px; background: rgba(255,255,255,0.2); }

/* 控制项 */
.control-items { margin-top: 10px; }
.control-row {
  display: flex; justify-content: space-between; align-items: center;
  background: rgba(255,255,255,0.1);
  padding: 0.75rem 1.25rem;
  border-radius: 1rem;
}

.control-btn {
  border: none;
  background: rgba(255,255,255,0.2);
  color: white;
  padding: 0.4rem 1.2rem;
  border-radius: 100px;
  font-weight: 700;
  font-size: 0.85rem;
  transition: all 0.3s ease;
  min-width: 70px;
}

.control-btn.active { background: #ffc107; color: #000; box-shadow: 0 4px 12px rgba(255, 193, 7, 0.4); }
.control-btn:hover:not(:disabled) { transform: scale(1.05); }

.status-pill {
  padding: 0.25rem 0.75rem;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 800;
  background: rgba(255,255,255,0.2);
}
.status-pill.high { color: #ffc107; }

/* 趋势图 */
.section-title { font-weight: 700; color: #1a1a1a; margin-bottom: 0.5rem; }
.section-line { width: 40px; height: 4px; background: #4facfe; border-radius: 2px; }

.custom-date-picker {
  border: 1px solid rgba(0,0,0,0.05);
  transition: all 0.3s ease;
}

.custom-date-picker:hover {
  box-shadow: 0 5px 15px rgba(0,0,0,0.05) !important;
  border-color: #4facfe;
}

.picker-label span {
  font-size: 0.8rem;
  white-space: nowrap;
}

.date-input {
  border: none;
  outline: none;
  font-size: 0.85rem;
  font-weight: 500;
  color: #495057;
  cursor: pointer;
  background: transparent;
  padding: 2px 5px;
  border-radius: 4px;
}

.date-input:focus {
  background: #f8f9fa;
  color: #4facfe;
}

.chart-box { border-radius: 1.5rem; }
.chart-element { height: 350px; width: 100%; }

/* 加载状态 */
.loader-wave {
  display: flex; justify-content: center; align-items: center; gap: 6px;
}
.loader-wave span {
  width: 8px; height: 8px; background: #4facfe; border-radius: 50%;
  animation: wave 1.2s infinite ease-in-out;
}
.loader-wave span:nth-child(2) { animation-delay: 0.1s; }
.loader-wave span:nth-child(3) { animation-delay: 0.2s; }
.loader-wave span:nth-child(4) { animation-delay: 0.3s; }

@keyframes wave {
  0%, 40%, 100% { transform: scaleY(0.4); }
  20% { transform: scaleY(2.0); }
}

/* 空状态 */
.empty-state-card { border: none; }
.icon-circle {
  width: 100px; height: 100px;
  background: #f0f7ff;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}

/* 错误通知 */
.error-toast {
  position: fixed; top: 2rem; right: 2rem;
  background: #dc3545; color: white;
  padding: 1rem 1.5rem; border-radius: 12px;
  display: flex; align-items: center;
  box-shadow: 0 10px 25px rgba(220, 53, 69, 0.3);
  z-index: 9999;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

@media (max-width: 991px) {
  .header-panel { text-align: center; }
  .status-badge { margin-top: 1rem; }
}
</style>
