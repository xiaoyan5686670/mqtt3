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

        <!-- 传感器卡片网格 - 动态生成 -->
        <div v-if="!loadingData" class="row g-4 mb-5">
          <!-- 重要指标（温度、湿度） -->
          <div v-for="sensor in dynamicPrioritySensors" :key="sensor.type" class="col-xl-3 col-md-6">
            <div class="sensor-glass-card" :class="getSensorClass(sensor.type)">
              <div class="card-overlay"></div>
              <div class="card-content">
                <div class="sensor-header mb-3">
                  <span class="sensor-label">{{ getDisplayName(sensor) }}</span>
                  <div class="sensor-icon-circle">
                    <i :class="getSensorIcon(sensor.type)"></i>
                  </div>
                </div>
                <div class="sensor-values text-center">
                  <div class="value-item main w-100">
                    <span class="number">{{ formatValue(sensor.value) }}</span>
                    <span class="unit">{{ sensor.unit }}</span>
                  </div>
                </div>
                <div class="sensor-footer mt-2">
                   <small class="text-white-50">原始ID: {{ sensor.type }}</small>
                </div>
              </div>
            </div>
          </div>

          <!-- 系统控制卡片 -->
          <div v-if="controlSensors.length > 0" class="col-xl-3 col-md-6">
            <div class="sensor-glass-card control">
              <div class="card-overlay"></div>
              <div class="card-content">
                <div class="sensor-header mb-3">
                  <span class="sensor-label">系统控制</span>
                  <div class="sensor-icon-circle">
                    <i class="fas fa-cogs"></i>
                  </div>
                </div>
                <div class="control-items">
                  <div v-for="sensor in controlSensors" :key="sensor.type" class="control-row mb-2">
                    <div class="control-info d-flex align-items-center">
                      <i class="fas" :class="[getControlIcon(sensor), sensor.value > 0 ? 'text-warning' : 'text-white-50']"></i>
                      <div class="ms-2">
                        <div class="small fw-bold">{{ getDisplayName(sensor) }}</div>
                        <div class="extra-small text-white-50">{{ sensor.type }}</div>
                      </div>
                    </div>
                    <button 
                      v-if="sensor.type.toLowerCase().includes('relay') || sensor.type.toLowerCase().includes('switch')"
                      class="control-btn" 
                      :class="{ 'active': sensor.value === 1, 'loading': sendingRelayId === `${selectedDeviceId}-${sensor.type}` }"
                      @click="toggleRelay(sensor)"
                      :disabled="sendingRelayId === `${selectedDeviceId}-${sensor.type}`"
                    >
                      <div v-if="sendingRelayId === `${selectedDeviceId}-${sensor.type}`" class="spinner-border spinner-border-sm"></div>
                      <span v-else>{{ sensor.value === 1 ? 'ON' : 'OFF' }}</span>
                    </button>
                    <div v-else class="status-pill" :class="sensor.value > 0 ? 'high' : 'low'">
                      {{ sensor.value > 0 ? 'HIGH' : 'LOW' }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 其他普通数据 -->
          <div v-for="sensor in otherSensors" :key="sensor.type" class="col-xl-3 col-md-6">
             <div class="sensor-glass-card other">
              <div class="card-overlay"></div>
              <div class="card-content">
                <div class="sensor-header mb-3">
                  <span class="sensor-label">{{ getDisplayName(sensor) }}</span>
                  <div class="sensor-icon-circle">
                    <i class="fas fa-microchip"></i>
                  </div>
                </div>
                <div class="sensor-values text-center">
                  <div class="value-item main w-100">
                    <span class="number">{{ formatValue(sensor.value) }}</span>
                    <span class="unit">{{ sensor.unit }}</span>
                  </div>
                </div>
                <div class="sensor-footer mt-2">
                   <small class="text-white-50">原始ID: {{ sensor.type }}</small>
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
                <input type="date" v-model="startDate" class="date-input" @change="refreshData">
                <span class="mx-2 text-muted">至</span>
                <input type="date" v-model="endDate" class="date-input" @change="refreshData">
              </div>
            </div>
          </div>
          <div class="row g-4">
            <div class="col-12">
              <div class="chart-box card border-0 shadow-sm">
                <div class="card-body p-4">
                  <div ref="chart1Ref" class="chart-element"></div>
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
          请从顶部面板选择一个已注册的物联网设备，系统将自动建立实时数据通道并为您展示动态监控图表。
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
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

export default {
  name: 'RealTimeData',
  setup() {
    const devices = ref([])
    const selectedDeviceId = ref('')
    const allSensors = ref([])
    const loadingData = ref(false)
    const error = ref('')
    const sendingRelayId = ref(null)
    const timeRange = ref('realtime')
    
    // 初始化日期区间 (用于月维度)
    const getInitialDateRange = () => {
      const now = new Date()
      const firstDay = new Date(now.getFullYear(), now.getMonth(), 1)
      const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0)
      const f = (d) => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
      return { start: f(firstDay), end: f(lastDay) }
    }
    const initialRange = getInitialDateRange()
    const startDate = ref(initialRange.start)
    const endDate = ref(initialRange.end)
    
    const chart1Ref = ref(null)
    let chart1 = null
    const chartData = ref({ timeStamps: [] })

    // 分类传感器
    const dynamicPrioritySensors = computed(() => {
      return allSensors.value.filter(s => {
        const t = s.type.toLowerCase()
        return (t.includes('temp') || t.includes('hum')) && !t.includes('relay')
      })
    })

    const controlSensors = computed(() => {
      return allSensors.value.filter(s => {
        const t = s.type.toLowerCase()
        return t.includes('relay') || t.includes('pb8') || t.includes('switch') || t.includes('level')
      })
    })

    const otherSensors = computed(() => {
      return allSensors.value.filter(s => {
        const t = s.type.toLowerCase()
        return !t.includes('temp') && !t.includes('hum') && !t.includes('relay') && !t.includes('pb8') && !t.includes('switch') && !t.includes('level')
      })
    })

    const getDisplayName = (sensor) => sensor.display_name || sensor.type
    
    const getSensorClass = (type) => {
      const t = type.toLowerCase()
      if (t.includes('temp')) return 'temperature'
      if (t.includes('hum')) return 'humidity'
      return 'other'
    }

    const getSensorIcon = (type) => {
      const t = type.toLowerCase()
      if (t.includes('temp')) return 'fas fa-temperature-high'
      if (t.includes('hum')) return 'fas fa-tint'
      return 'fas fa-microchip'
    }

    const getControlIcon = (sensor) => {
      const t = sensor.type.toLowerCase()
      if (t.includes('relay') || t.includes('switch')) return 'fa-plug'
      return 'fa-bolt'
    }

    const formatValue = (val) => typeof val === 'number' ? val.toFixed(1) : val

    const fetchDevices = async () => {
      try {
        const res = await axios.get('/api/devices')
        devices.value = res.data
      } catch (e) { console.error(e) }
    }

    const fetchRealTimeData = async () => {
      if (!selectedDeviceId.value) return
      if (allSensors.value.length === 0) loadingData.value = true
      try {
        const res = await axios.get(`/api/devices/${selectedDeviceId.value}/latest-sensors`)
        allSensors.value = res.data
        if (timeRange.value === 'realtime') updateChartsRealtime()
      } catch (err) { error.value = err.message } finally { loadingData.value = false }
    }

    // 重新加载历史数据逻辑
    const loadHistoryData = async () => {
      if (!selectedDeviceId.value) return
      loadingData.value = true
      error.value = ''
      try {
        const params = { limit: timeRange.value === 'month' ? 5000 : 2000 }
        if (timeRange.value === 'month') {
          params.start_time = `${startDate.value}T00:00:00`
          params.end_time = `${endDate.value}T23:59:59`
        } else {
          params.time_range = timeRange.value
        }

        const res = await axios.get(`/api/sensors/device/${selectedDeviceId.value}/history`, { params })
        const sensors = res.data || []
        
        processHistoryData(sensors)
      } catch (e) {
        console.error('加载历史数据失败:', e)
        error.value = `加载历史数据失败: ${e.message}`
      } finally {
        loadingData.value = false
        // 关键修复：确保在 loadingData 变为 false 且 Vue 完成 DOM 更新后再渲染图表
        nextTick(() => {
          renderCharts(true)
        })
      }
    }

    // 独立的数据处理函数，实现日/周/月聚合逻辑
    const processHistoryData = (sensors) => {
      const sensorNameMap = {}
      const timeDataMap = {}

      sensors.forEach(item => {
        const val = parseFloat(item.value)
        if (isNaN(val)) return
        
        let ts = item.timestamp
        if (typeof ts === 'string') {
          ts = ts.replace(' ', 'T')
          if (!ts.includes('Z') && !ts.includes('+')) ts += 'Z'
        }
        const dt = new Date(ts)
        if (isNaN(dt.getTime())) return

        let label = ''
        if (timeRange.value === 'day') {
          label = `${String(dt.getHours()).padStart(2, '0')}:00`
        } else if (timeRange.value === 'week') {
          label = `${String(dt.getMonth() + 1).padStart(2, '0')}/${String(dt.getDate()).padStart(2, '0')}`
        } else if (timeRange.value === 'month') {
          label = `${String(dt.getMonth() + 1).padStart(2, '0')}/${String(dt.getDate()).padStart(2, '0')}`
        }
        
        if (!timeDataMap[label]) timeDataMap[label] = {}
        if (!timeDataMap[label][item.type]) timeDataMap[label][item.type] = []
        timeDataMap[label][item.type].push(val)
        sensorNameMap[item.type] = item.display_name || item.type
      })

      // 生成标准时间轴标签
      let timeLabels = []
      if (timeRange.value === 'day') {
        timeLabels = Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2, '0')}:00`)
      } else if (timeRange.value === 'week') {
        const now = new Date()
        for (let i = 6; i >= 0; i--) {
          const d = new Date(now)
          d.setDate(now.getDate() - i)
          timeLabels.push(`${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`)
        }
      } else if (timeRange.value === 'month') {
        const start = new Date(startDate.value + 'T00:00:00')
        const end = new Date(endDate.value + 'T23:59:59')
        const curr = new Date(start)
        while (curr <= end) {
          timeLabels.push(`${String(curr.getMonth() + 1).padStart(2, '0')}/${String(curr.getDate()).padStart(2, '0')}`)
          curr.setDate(curr.getDate() + 1)
        }
      }

      // 计算平均值并构建系列
      const finalSeries = Object.keys(sensorNameMap)
        .filter(type => {
          const lowerType = type.toLowerCase()
          return !lowerType.includes('relay') && !lowerType.includes('switch') && !lowerType.includes('pb8') && !lowerType.includes('level')
        })
        .map(type => {
          return {
            name: sensorNameMap[type],
            type: 'line',
            data: timeLabels.map(label => {
              const points = timeDataMap[label]?.[type]
              if (!points || points.length === 0) return null
              return points.reduce((a, b) => a + b, 0) / points.length
            }),
            smooth: true,
            showSymbol: false,
            connectNulls: false
          }
        })
        .filter(s => s.data && s.data.some(v => v !== null))
      
      chartData.value = { 
        timeStamps: timeLabels, 
        historySeries: finalSeries 
      }
    }

    const updateChartsRealtime = () => {
      const now = new Date().toLocaleTimeString()
      if (!chartData.value.timeStamps) chartData.value.timeStamps = []
      chartData.value.timeStamps.push(now)
      if (chartData.value.timeStamps.length > 30) chartData.value.timeStamps.shift()

      allSensors.value.forEach(s => {
        if (!chartData.value[s.type]) chartData.value[s.type] = []
        chartData.value[s.type].push(s.value)
        if (chartData.value[s.type].length > 30) chartData.value[s.type].shift()
      })
      renderCharts(false)
    }

    const renderCharts = (isHistory = false) => {
      nextTick(() => {
        if (!chart1Ref.value) return
        if (!chart1) {
          chart1 = echarts.init(chart1Ref.value)
          window.addEventListener('resize', () => chart1 && chart1.resize())
        }
        
        let series = []
        let timeStamps = []

        if (isHistory) {
          timeStamps = chartData.value.timeStamps || []
          series = chartData.value.historySeries || []
        } else {
          timeStamps = [...chartData.value.timeStamps] || []
          series = allSensors.value
            .filter(s => typeof s.value === 'number' && 
              !s.type.toLowerCase().includes('relay') && 
              !s.type.toLowerCase().includes('switch') && 
              !s.type.toLowerCase().includes('pb8'))
            .map(s => ({
              name: getDisplayName(s),
              type: 'line',
              data: [...(chartData.value[s.type] || [])],
              smooth: true,
              showSymbol: false,
              areaStyle: { opacity: 0.05 }
            }))
        }

        if (series.length === 0 || timeStamps.length === 0) {
          chart1.setOption({
            title: { text: '暂无数据', left: 'center', top: 'middle', textStyle: { color: '#999', fontSize: 14 } },
            xAxis: { show: false },
            yAxis: { show: false },
            series: []
          }, { notMerge: true })
          return
        }

        chart1.setOption({
          title: { show: false },
          tooltip: { 
            trigger: 'axis',
            confine: true,
            formatter: (params) => {
              if (!params || params.length === 0) return ''
              let res = `<div style="margin-bottom: 5px; font-weight: bold;">${params[0].axisValue}</div>`
              params.forEach(p => {
                if (p.value !== null && p.value !== undefined && p.value !== '') {
                  res += `<div style="display: flex; align-items: center; margin: 3px 0;">
                    <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background-color:${p.color};margin-right:8px;"></span>
                    <span style="flex: 1;">${p.seriesName}:</span>
                    <span style="font-weight: bold; margin-left: 15px;">${typeof p.value === 'number' ? p.value.toFixed(2) : p.value}</span>
                  </div>`
                }
              })
              return res
            }
          },
          legend: { 
            data: series.map(s => s.name), 
            top: 0, 
            type: 'scroll',
            orient: 'horizontal',
            textStyle: { color: '#333' }
          },
          grid: { top: 60, left: '3%', right: '4%', bottom: '5%', containLabel: true },
          xAxis: { 
            type: 'category', 
            data: timeStamps,
            axisLabel: {
              interval: timeRange.value === 'day' ? 2 : timeRange.value === 'week' ? 1 : 'auto',
              rotate: timeRange.value === 'month' ? 45 : 0,
              fontSize: 12
            }
          },
          yAxis: { 
            type: 'value', 
            scale: true,
            axisLabel: {
              formatter: '{value}'
            }
          },
          series: series
        }, { notMerge: true })
      })
    }

    const toggleRelay = async (sensor) => {
      const device = devices.value.find(d => d.id == selectedDeviceId.value)
      if (!device) return
      const sensorKey = `${device.id}-${sensor.type}`
      sendingRelayId.value = sensorKey
      try {
        const topic = device.publish_topic || `pc/${device.id}`
        const message = sensor.value > 0 ? 'relayoff' : 'relayon'
        await axios.post('/api/mqtt-publish/publish', { topic, message })
        setTimeout(fetchRealTimeData, 500)
      } catch (e) { error.value = e.message } finally { sendingRelayId.value = null }
    }

    const onDeviceChange = () => {
      // 重置图表数据
      chartData.value = { timeStamps: [], historySeries: [] }
      allSensors.value = []
      if (chart1) {
        chart1.clear()
        chart1.dispose()
        chart1 = null
      }
      if (selectedDeviceId.value) {
        if (timeRange.value === 'realtime') fetchRealTimeData()
        else loadHistoryData()
      }
    }

    const setTimeRange = (r) => { 
      timeRange.value = r
      onDeviceChange() 
    }
    const refreshData = () => {
      if (timeRange.value === 'realtime') fetchRealTimeData()
      else loadHistoryData()
    }
    const getRangeIcon = (r) => ({ realtime: 'fas fa-bolt', day: 'fas fa-calendar-day', week: 'fas fa-calendar-week', month: 'fas fa-calendar-alt' }[r])
    const getRangeText = (r) => ({ realtime: '实时', day: '日维度', week: '周趋势', month: '月分析' }[r])

    onMounted(() => {
      fetchDevices()
      window.realtimeInterval = setInterval(() => {
        if (selectedDeviceId.value && timeRange.value === 'realtime') fetchRealTimeData()
      }, 3000)
    })
    onUnmounted(() => clearInterval(window.realtimeInterval))

    return {
      devices, selectedDeviceId, allSensors, loadingData, error, sendingRelayId,
      dynamicPrioritySensors, controlSensors, otherSensors, getDisplayName,
      getSensorClass, getSensorIcon, getControlIcon, formatValue,
      onDeviceChange, setTimeRange, refreshData, getRangeIcon, getRangeText, toggleRelay,
      chart1Ref, timeRange, startDate, endDate
    }
  }
}
</script>

<style scoped>
.real-time-data { min-height: 100vh; background-color: #f0f2f5; }
.header-panel { border: none; border-radius: 1.25rem; }
.title-icon { width: 44px; height: 44px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 10px; display: flex; align-items: center; justify-content: center; }
.status-badge { display: inline-flex; align-items: center; padding: 0.4rem 1rem; background: #f8f9fa; border-radius: 100px; font-size: 0.8rem; font-weight: 600; color: #6c757d; }
.status-badge.active { background: rgba(40, 167, 69, 0.1); color: #28a745; }
.pulse-dot { width: 6px; height: 6px; background-color: currentColor; border-radius: 50%; margin-right: 8px; }
.sensor-glass-card { position: relative; padding: 1.5rem; border-radius: 1.5rem; overflow: hidden; color: white; min-height: 180px; box-shadow: 0 8px 20px rgba(0,0,0,0.08); }
.sensor-glass-card.temperature { background: linear-gradient(135deg, #ff6b6b 0%, #f06595 100%); }
.sensor-glass-card.humidity { background: linear-gradient(135deg, #37b24d 0%, #2f9e44 100%); }
.sensor-glass-card.control { background: linear-gradient(135deg, #1c7ed6 0%, #1971c2 100%); }
.sensor-glass-card.other { background: linear-gradient(135deg, #6c757d 0%, #495057 100%); }
.card-overlay { position: absolute; top: -10%; right: -5%; width: 120px; height: 120px; background: rgba(255,255,255,0.1); border-radius: 50%; }
.sensor-label { font-size: 1rem; font-weight: 600; }
.sensor-icon-circle { width: 36px; height: 36px; background: rgba(255,255,255,0.2); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1rem; }
.sensor-values .number { font-size: 2.2rem; font-weight: 800; }
.sensor-values .unit { font-size: 1rem; margin-left: 4px; opacity: 0.8; }
.extra-small { font-size: 0.65rem; }
.control-row { display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.1); padding: 0.5rem 0.75rem; border-radius: 0.75rem; }
.control-btn { border: none; background: rgba(255,255,255,0.2); color: white; padding: 0.3rem 0.8rem; border-radius: 100px; font-weight: 700; font-size: 0.75rem; min-width: 60px; }
.control-btn.active { background: #ffc107; color: #000; }
.status-pill { padding: 0.2rem 0.6rem; border-radius: 100px; font-size: 0.7rem; font-weight: 800; background: rgba(255,255,255,0.2); }
.chart-box { border-radius: 1.25rem; }
.chart-element { height: 450px; width: 100%; }
.loader-wave { display: flex; justify-content: center; gap: 4px; }
.loader-wave span { width: 6px; height: 6px; background: #4facfe; border-radius: 50%; animation: wave 1.2s infinite ease-in-out; }
@keyframes wave { 0%, 40%, 100% { transform: scaleY(0.4); } 20% { transform: scaleY(1.8); } }
</style>
