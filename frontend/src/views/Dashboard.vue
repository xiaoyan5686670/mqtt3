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
    
    <!-- 统计卡片区域 -->
    <div class="stats-container mb-4">
      <div class="row g-3">
        <div class="col-md-4">
          <div class="stat-card stat-card-total">
            <div class="stat-icon">
              <i class="fas fa-server"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ devices.length }}</div>
              <div class="stat-label">总设备数</div>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="stat-card stat-card-online">
            <div class="stat-icon">
              <i class="fas fa-check-circle"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ onlineDevices }}</div>
              <div class="stat-label">在线设备</div>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="stat-card stat-card-offline">
            <div class="stat-icon">
              <i class="fas fa-times-circle"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ offlineDevices }}</div>
              <div class="stat-label">离线设备</div>
            </div>
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

    <!-- STM32_4 温度监控专区 -->
    <div v-if="stm32Device" class="row mb-4">
      <div class="col-12">
        <div class="card temperature-monitor-card">
          <div class="card-header bg-gradient-primary text-white">
            <h5 class="mb-0">
              <i class="fas fa-thermometer-half me-2"></i>
              {{ getDeviceDisplayName(stm32Device.device) }} - 温度监控
            </h5>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <!-- 压缩机1组件 -->
              <div class="col-xl-6 col-lg-6 col-md-12 col-sm-12">
                <div class="compressor-group" :class="getCompressorGroupClass(1)">
                  <div class="compressor-header">
                    <div class="compressor-icon-wrapper">
                      <i 
                        class="fas fa-fan compressor-fan-icon" 
                        :class="{ 'fan-rotating': isCompressorNormal(1) }"
                      ></i>
                    </div>
                    <h6 class="compressor-title">压缩机1 (Compressor 1)</h6>
                  </div>
                  <div class="temperature-pair">
                    <div class="temp-item">
                      <div class="temp-item-label">
                        <i class="fas fa-arrow-down me-1"></i>入口温度
                      </div>
                      <div class="temp-item-value" :class="{ 'temp-danger': !isCompressorNormal(1) }">
                        {{ getCompressorTemp(1, 'in') }}
                        <span class="temp-unit">℃</span>
                      </div>
                    </div>
                    <div class="temp-arrow">
                      <i class="fas fa-arrow-right"></i>
                    </div>
                    <div class="temp-item">
                      <div class="temp-item-label">
                        <i class="fas fa-arrow-up me-1"></i>出口温度
                      </div>
                      <div class="temp-item-value" :class="{ 'temp-danger': !isCompressorNormal(1) }">
                        {{ getCompressorTemp(1, 'out') }}
                        <span class="temp-unit">℃</span>
                      </div>
                    </div>
                  </div>
                  <div class="compressor-status">
                    <span v-if="isCompressorNormal(1)" class="badge bg-success">
                      <i class="fas fa-check-circle me-1"></i>正常运行
                    </span>
                    <span v-else class="badge bg-danger">
                      <i class="fas fa-exclamation-triangle me-1"></i>温度异常 (出口 < 入口)
                    </span>
                  </div>
                </div>
              </div>
              
              <!-- 压缩机2组件 -->
              <div class="col-xl-6 col-lg-6 col-md-12 col-sm-12">
                <div class="compressor-group" :class="getCompressorGroupClass(2)">
                  <div class="compressor-header">
                    <div class="compressor-icon-wrapper">
                      <i 
                        class="fas fa-fan compressor-fan-icon" 
                        :class="{ 'fan-rotating': isCompressorNormal(2) }"
                      ></i>
                    </div>
                    <h6 class="compressor-title">压缩机2 (Compressor 2)</h6>
                  </div>
                  <div class="temperature-pair">
                    <div class="temp-item">
                      <div class="temp-item-label">
                        <i class="fas fa-arrow-down me-1"></i>入口温度
                      </div>
                      <div class="temp-item-value" :class="{ 'temp-danger': !isCompressorNormal(2) }">
                        {{ getCompressorTemp(2, 'in') }}
                        <span class="temp-unit">℃</span>
                      </div>
                    </div>
                    <div class="temp-arrow">
                      <i class="fas fa-arrow-right"></i>
                    </div>
                    <div class="temp-item">
                      <div class="temp-item-label">
                        <i class="fas fa-arrow-up me-1"></i>出口温度
                      </div>
                      <div class="temp-item-value" :class="{ 'temp-danger': !isCompressorNormal(2) }">
                        {{ getCompressorTemp(2, 'out') }}
                        <span class="temp-unit">℃</span>
                      </div>
                    </div>
                  </div>
                  <div class="compressor-status">
                    <span v-if="isCompressorNormal(2)" class="badge bg-success">
                      <i class="fas fa-check-circle me-1"></i>正常运行
                    </span>
                    <span v-else class="badge bg-danger">
                      <i class="fas fa-exclamation-triangle me-1"></i>温度异常 (出口 < 入口)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
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
                      <!-- 在线状态指示器 -->
                      <span 
                        class="status-indicator me-2" 
                        :class="deviceData.isOnline ? 'status-online' : 'status-offline'"
                        :title="deviceData.isOnline ? '在线' : '离线'"
                      >
                        <i class="fas fa-circle"></i>
                      </span>
                      <h6 class="mb-0 me-2 device-name">
                        <i class="fas fa-microchip me-1"></i>
                        <span v-if="editingDeviceId !== deviceData.device.id" class="device-name-wrapper">
                          <span 
                            class="device-name-text" 
                            :title="getDeviceDisplayName(deviceData.device)"
                          >
                            {{ getDeviceDisplayName(deviceData.device) }}
                          </span>
                          <button 
                            v-if="authStore.canEdit"
                            class="btn-edit-device"
                            @click.stop="startEditDevice(deviceData.device)"
                            title="编辑设备名称"
                          >
                            <i class="fas fa-edit"></i>
                          </button>
                        </span>
                        <div v-else class="device-edit-input">
                          <input
                            type="text"
                            v-model="editingDeviceName"
                            @keyup.enter="saveDeviceName(deviceData.device.id)"
                            @keyup.esc="cancelEditDevice"
                            @focus="$event.target.select()"
                            class="form-control form-control-sm"
                            :maxlength="50"
                            :data-device-id="deviceData.device.id"
                          />
                          <button 
                            class="btn btn-sm btn-success ms-1"
                            @click="saveDeviceName(deviceData.device.id)"
                            title="保存"
                          >
                            <i class="fas fa-check"></i>
                          </button>
                          <button 
                            class="btn btn-sm btn-secondary ms-1"
                            @click="cancelEditDevice"
                            title="取消"
                          >
                            <i class="fas fa-times"></i>
                          </button>
                        </div>
                      </h6>
                    </div>
                    <div class="d-flex flex-wrap gap-1 mb-1">
                      <span 
                        v-if="deviceData.device.device_type"
                        class="badge bg-info"
                      >
                        {{ deviceData.device.device_type }}
                      </span>
                    </div>
                    <small class="text-muted device-location-wrapper">
                      <i class="fas fa-map-marker-alt me-1"></i>
                      <span 
                        class="device-location" 
                        :title="deviceData.device.location || '未知位置'"
                      >
                        {{ deviceData.device.location || '未知位置' }}
                      </span>
                    </small>
                  </div>
                  <div class="device-icon-area">
                    <!-- 继电器输入状态指示器（只读，显示外部输入状态） -->
                    <div 
                      class="relay-in-status-indicator mb-2"
                      :title="getRelayInDisplayName(deviceData.device) + '状态（只读）: ' + (getRelayInStatusValue(deviceData.sensors) > 0 ? 'ON（有输入）' : 'OFF（无输入）')"
                    >
                      <div class="relay-label-wrapper">
                        <span v-if="editingRelayInId !== deviceData.device.id" class="relay-in-name-wrapper">
                          <span class="status-label" :title="getRelayInDisplayName(deviceData.device)">
                            {{ getRelayInDisplayName(deviceData.device) }}
                          </span>
                          <button 
                            v-if="authStore.canEdit"
                            class="btn-edit-relay-in"
                            @click.stop="startEditRelayIn(deviceData.device)"
                            title="编辑名称"
                          >
                            <i class="fas fa-edit"></i>
                          </button>
                        </span>
                        <div v-else class="relay-in-edit-input">
                          <input
                            type="text"
                            v-model="editingRelayInName"
                            @keyup.enter="saveRelayInName(deviceData.device.id)"
                            @keyup.esc="cancelEditRelayIn"
                            @focus="$event.target.select()"
                            class="form-control form-control-sm"
                            :maxlength="50"
                            placeholder="继电器输入"
                          />
                          <button 
                            class="btn btn-sm btn-success ms-1"
                            @click="saveRelayInName(deviceData.device.id)"
                            title="保存"
                          >
                            <i class="fas fa-check"></i>
                          </button>
                          <button 
                            class="btn btn-sm btn-secondary ms-1"
                            @click="cancelEditRelayIn"
                            title="取消"
                          >
                            <i class="fas fa-times"></i>
                          </button>
                        </div>
                      </div>
                      <div 
                        class="status-icon"
                        :class="getRelayInStatusValue(deviceData.sensors) > 0 ? 'status-on' : 'status-off'"
                      >
                        <i class="fas fa-plug"></i>
                        <span class="status-text">
                          {{ getRelayInStatusValue(deviceData.sensors) > 0 ? 'ON' : 'OFF' }}
                        </span>
                      </div>
                    </div>
                    <div class="device-icon">
                      <i class="fas fa-server fa-2x text-primary"></i>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 卡片主体：关键数据指标（温度、湿度优先） -->
              <div class="card-body py-2 px-3">
                <!-- 重要指标：美观的 Mini 分组 (Air & Comp) -->
                <div 
                  v-if="hasGroupsOrPriority(deviceData.sensors)" 
                  class="priority-metrics-container"
                  @mouseenter="hoveredDeviceIdForRestore = deviceData.device.id"
                  @mouseleave="hoveredDeviceIdForRestore = null"
                >
                  <div 
                    v-if="hasHiddenGroupsForDevice(deviceData.device.id) && hoveredDeviceIdForRestore === deviceData.device.id" 
                    class="restore-button-wrapper"
                  >
                    <button type="button" class="btn-restore-subtle" @click="restoreGroups(deviceData.device.id)" title="恢复该设备下所有已关闭的分组">
                      <i class="fas fa-undo me-1"></i>还原
                    </button>
                  </div>
                  <div class="priority-metrics mb-2">
                    <div class="row g-2">
                    <div 
                      v-for="group in getVisibleGroups(deviceData)" 
                      :key="`${group.groupType}-${group.number}`"
                      class="col-12"
                    >
                      <!-- Air Group: 环境组 (左右并排) -->
                      <div v-if="group.groupType === 'air'" class="mini-group-card status-default">
                        <div class="mini-group-header">
                          <span class="mini-title"><i class="fas fa-layer-group me-1"></i>环境组 {{ group.number }}</span>
                          <button type="button" class="btn-group-close" title="关闭此分组" @click="hideGroup(deviceData.device.id, group)">
                            <i class="fas fa-times"></i>
                          </button>
                        </div>
                        <div class="mini-body">
                          <!-- 温度 -->
                          <div v-if="group.temp" class="mini-sensor-item">
                            <div class="mini-label-container">
                              <template v-if="editingSensorId !== `${deviceData.device.id}-${group.temp.type}`">
                                <div class="mini-label text-truncate" :title="getSensorDisplayName(group.temp)">
                                  <i class="fas fa-thermometer-half me-1"></i>{{ getSensorDisplayName(group.temp) }}
                                </div>
                                <button v-if="authStore.canEdit" class="mini-edit-btn" @click.stop="startEditSensor(deviceData.device.id, group.temp)" title="编辑"><i class="fas fa-pen"></i></button>
                              </template>
                              <div v-else class="mini-edit-box" @click.stop>
                                <input type="text" v-model="editingSensorName" @keyup.enter="saveSensorName(deviceData.device.id, group.temp)" @keyup.esc="cancelEditSensor" class="form-control form-control-sm mini-input" />
                                <button class="btn-mini-action text-success" @click="saveSensorName(deviceData.device.id, group.temp)"><i class="fas fa-check"></i></button>
                                <button class="btn-mini-action text-secondary" @click="cancelEditSensor"><i class="fas fa-times"></i></button>
                              </div>
                            </div>
                            <div class="mini-value text-danger" :title="getSensorDisplayName(group.temp)">
                              {{ formatSensorValue(group.temp.value) }}<span class="unit">{{ group.temp.unit || '℃' }}</span>
                            </div>
                          </div>
                          <div class="divider-vertical"></div>
                          <!-- 湿度 -->
                          <div v-if="group.hum" class="mini-sensor-item">
                            <div class="mini-label-container">
                              <template v-if="editingSensorId !== `${deviceData.device.id}-${group.hum.type}`">
                                <div class="mini-label text-truncate" :title="getSensorDisplayName(group.hum)">
                                  <i class="fas fa-tint me-1"></i>{{ getSensorDisplayName(group.hum) }}
                                </div>
                                <button v-if="authStore.canEdit" class="mini-edit-btn" @click.stop="startEditSensor(deviceData.device.id, group.hum)" title="编辑"><i class="fas fa-pen"></i></button>
                              </template>
                              <div v-else class="mini-edit-box" @click.stop>
                                <input type="text" v-model="editingSensorName" @keyup.enter="saveSensorName(deviceData.device.id, group.hum)" @keyup.esc="cancelEditSensor" class="form-control form-control-sm mini-input" />
                                <button class="btn-mini-action text-success" @click="saveSensorName(deviceData.device.id, group.hum)"><i class="fas fa-check"></i></button>
                                <button class="btn-mini-action text-secondary" @click="cancelEditSensor"><i class="fas fa-times"></i></button>
                              </div>
                            </div>
                            <div class="mini-value text-primary" :title="getSensorDisplayName(group.hum)">
                              {{ formatSensorValue(group.hum.value) }}<span class="unit">{{ group.hum.unit || '%' }}</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      <!-- Comp Group: 流程组 (入口 -> 出口) -->
                      <div v-else-if="group.groupType === 'comp'" class="mini-group-card" :class="group.out && group.in && group.out.value >= group.in.value ? 'status-normal' : 'status-abnormal'">
                        <div class="mini-group-header">
                          <span class="mini-title"><i class="fas fa-fan me-1"></i>流程组 {{ group.number }}</span>
                          <button type="button" class="btn-group-close" title="关闭此分组" @click="hideGroup(deviceData.device.id, group)">
                            <i class="fas fa-times"></i>
                          </button>
                        </div>
                        <div class="mini-body">
                          <!-- 入口 -->
                          <div v-if="group.in" class="mini-sensor-item">
                            <div class="mini-label-container">
                              <template v-if="editingSensorId !== `${deviceData.device.id}-${group.in.type}`">
                                <div class="mini-label text-truncate" :title="getSensorDisplayName(group.in)">
                                  {{ getSensorDisplayName(group.in) }}
                                </div>
                                <button v-if="authStore.canEdit" class="mini-edit-btn" @click.stop="startEditSensor(deviceData.device.id, group.in)" title="编辑"><i class="fas fa-pen"></i></button>
                              </template>
                              <div v-else class="mini-edit-box" @click.stop>
                                <input type="text" v-model="editingSensorName" @keyup.enter="saveSensorName(deviceData.device.id, group.in)" @keyup.esc="cancelEditSensor" class="form-control form-control-sm mini-input" />
                                <button class="btn-mini-action text-success" @click="saveSensorName(deviceData.device.id, group.in)"><i class="fas fa-check"></i></button>
                                <button class="btn-mini-action text-secondary" @click="cancelEditSensor"><i class="fas fa-times"></i></button>
                              </div>
                            </div>
                            <div class="mini-value" :title="getSensorDisplayName(group.in)">
                              {{ formatSensorValue(group.in.value) }}<span class="unit">{{ group.in.unit || '℃' }}</span>
                            </div>
                          </div>
                          
                          <!-- 箭头 -->
                          <i class="fas fa-arrow-right flow-arrow"></i>

                          <!-- 出口 -->
                          <div v-if="group.out" class="mini-sensor-item">
                            <div class="mini-label-container">
                              <template v-if="editingSensorId !== `${deviceData.device.id}-${group.out.type}`">
                                <div class="mini-label text-truncate" :title="getSensorDisplayName(group.out)">
                                  {{ getSensorDisplayName(group.out) }}
                                </div>
                                <button v-if="authStore.canEdit" class="mini-edit-btn" @click.stop="startEditSensor(deviceData.device.id, group.out)" title="编辑"><i class="fas fa-pen"></i></button>
                              </template>
                              <div v-else class="mini-edit-box" @click.stop>
                                <input type="text" v-model="editingSensorName" @keyup.enter="saveSensorName(deviceData.device.id, group.out)" @keyup.esc="cancelEditSensor" class="form-control form-control-sm mini-input" />
                                <button class="btn-mini-action text-success" @click="saveSensorName(deviceData.device.id, group.out)"><i class="fas fa-check"></i></button>
                                <button class="btn-mini-action text-secondary" @click="cancelEditSensor"><i class="fas fa-times"></i></button>
                              </div>
                            </div>
                            <div class="mini-value" :class="group.out && group.in && group.out.value < group.in.value ? 'text-danger' : 'text-success'" :title="getSensorDisplayName(group.out)">
                              {{ formatSensorValue(group.out.value) }}<span class="unit">{{ group.out.unit || '℃' }}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- 未分组的传感器 (保持 Mini 风格) -->
                    <div 
                      v-for="sensor in getSensorGroups(deviceData.sensors).ungrouped" 
                      :key="sensor.id"
                      class="col-6"
                    >
                      <div class="metric-card">
                        <div class="metric-label">
                          <!-- 这里的结构需要保持与原有逻辑兼容，或者也改造成 mini 风格，但为了风险控制，暂时保持 原有结构 但优化样式 -->
                          <span class="text-truncate" :title="getSensorDisplayName(sensor)">
                             {{ getSensorDisplayName(sensor) }}
                          </span>
                           <button v-if="authStore.canEdit" class="mini-edit-btn float-end" @click.stop="startEditSensor(deviceData.device.id, sensor)"><i class="fas fa-pen"></i></button>
                        </div>
                        <div class="metric-value">
                          {{ formatSensorValue(sensor.value) }}
                          <span class="metric-unit">{{ sensor.unit || '' }}</span>
                        </div>
                         <!-- 简易进度条 -->
                        <div class="metric-bar">
                           <div class="metric-progress" :class="getSensorStatusClass(sensor)" :style="{ width: getSensorPercentage(sensor) + '%' }"></div>
                        </div>
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
                    <div class="d-flex justify-content-between align-items-center sensor-row-content">
                      <span class="sensor-label">
                        <span v-if="editingSensorId !== `${deviceData.device.id}-${sensor.type}`" class="sensor-name-wrapper">
                          <span 
                            class="sensor-label-text" 
                            :title="getSensorDisplayName(sensor)"
                          >
                            {{ getSensorDisplayName(sensor) }}
                          </span>
                          <button 
                            v-if="authStore.canEdit"
                            class="btn-edit-sensor"
                            @click.stop="startEditSensor(deviceData.device.id, sensor)"
                            title="编辑名称"
                          >
                            <i class="fas fa-edit"></i>
                          </button>
                        </span>
                        <div v-else class="sensor-edit-input">
                          <input
                            type="text"
                            v-model="editingSensorName"
                            @keyup.enter="saveSensorName(deviceData.device.id, sensor)"
                            @keyup.esc="cancelEditSensor"
                            @focus="$event.target.select()"
                            class="form-control form-control-sm"
                            :maxlength="50"
                            :data-sensor-key="`${deviceData.device.id}-${sensor.type}`"
                          />
                          <button 
                            class="btn btn-sm btn-success ms-1"
                            @click="saveSensorName(deviceData.device.id, sensor)"
                            title="保存"
                          >
                            <i class="fas fa-check"></i>
                          </button>
                          <button 
                            class="btn btn-sm btn-secondary ms-1"
                            @click="cancelEditSensor"
                            title="取消"
                          >
                            <i class="fas fa-times"></i>
                          </button>
                        </div>
                      </span>
                      <div class="d-flex align-items-center gap-2 sensor-value-actions">
                        <span 
                          class="sensor-value-small me-2" 
                          :title="`${formatSensorValue(sensor.value)}${sensor.unit || ''}`"
                        >
                          {{ formatSensorValue(sensor.value) }}{{ sensor.unit || '' }}
                        </span>
                        <span 
                          v-if="isRelayType(sensor.type) || sensor.type.toLowerCase().includes('level')"
                          class="badge badge-sm"
                          :class="sensor.value > 0 ? 'bg-success' : 'bg-secondary'"
                        >
                          {{ sensor.value > 0 ? 'ON' : 'OFF' }}
                        </span>
                        <!-- 继电器控制按钮（排除只读的继电器输入） -->
                        <button 
                          v-if="isRelayType(sensor.type) && !isReadOnlyRelayInput(sensor.type) && authStore.canEdit"
                          class="btn btn-sm relay-toggle-btn"
                          :class="sensor.value > 0 ? 'btn-warning' : 'btn-success'"
                          @click.stop.prevent="toggleRelay(deviceData.device, sensor)"
                          :disabled="isRelaySending(deviceData.device.id, sensor.type)"
                          :title="sensor.value > 0 ? '关闭继电器' : '开启继电器'"
                        >
                          <span v-if="isRelaySending(deviceData.device.id, sensor.type)">
                            <span class="spinner-border spinner-border-sm me-1" role="status"></span>
                          </span>
                          <span v-else>
                            <i class="fas" :class="sensor.value > 0 ? 'fa-power-off' : 'fa-toggle-on'"></i>
                            {{ sensor.value > 0 ? '关闭' : '开启' }}
                          </span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div v-if="!deviceData.sensors || deviceData.sensors.length === 0" class="text-center text-muted py-2">
                  <small><i class="fas fa-exclamation-circle me-1"></i>暂无数据</small>
                </div>
              </div>
              
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
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Dashboard',
  setup() {
    const authStore = useAuthStore()
    const devices = ref([])
    const devicesWithSensors = ref([])
    const filteredDevices = ref([])
    const isLoading = ref(false)
    const searchKeyword = ref('')
    const editingSensorId = ref(null)
    const editingSensorName = ref('')
    const editingDeviceId = ref(null)
    const editingDeviceName = ref('')
    const editingRelayInId = ref(null)
    const editingRelayInName = ref('')
    const sendingRelayId = ref(null)
    const relayToggleLock = ref(new Set())
    const relayExpectedStates = ref(new Map())
    const allTopicConfigs = ref([])
    const STORAGE_KEY_HIDDEN_GROUPS = 'dashboard_hidden_groups'
    
    // 从 localStorage 加载已隐藏的分组
    const loadHiddenGroups = () => {
      try {
        const stored = localStorage.getItem(STORAGE_KEY_HIDDEN_GROUPS)
        if (stored) {
          const keys = JSON.parse(stored)
          return new Set(keys)
        }
      } catch (e) {
        console.warn('加载隐藏分组状态失败:', e)
      }
      return new Set()
    }
    
    // 保存到 localStorage
    const saveHiddenGroups = (keys) => {
      try {
        localStorage.setItem(STORAGE_KEY_HIDDEN_GROUPS, JSON.stringify([...keys]))
      } catch (e) {
        console.warn('保存隐藏分组状态失败:', e)
      }
    }

    const hiddenGroupKeys = ref(loadHiddenGroups()) // 'deviceId-groupType-number' 已隐藏的分组
    const hoveredDeviceIdForRestore = ref(null) // 鼠标悬停时显示还原按钮的设备 ID
    let refreshInterval = null

    const groupKey = (deviceId, group) => `${deviceId}-${group.groupType}-${group.number}`
    const isGroupHidden = (deviceId, group) => hiddenGroupKeys.value.has(groupKey(deviceId, group))
    const hideGroup = (deviceId, group) => {
      hiddenGroupKeys.value = new Set([...hiddenGroupKeys.value, groupKey(deviceId, group)])
      saveHiddenGroups(hiddenGroupKeys.value)
    }
    const restoreGroups = (deviceId) => {
      const pre = `${deviceId}-`
      hiddenGroupKeys.value = new Set([...hiddenGroupKeys.value].filter((k) => !k.startsWith(pre)))
      saveHiddenGroups(hiddenGroupKeys.value)
    }
    /** 该设备是否有被关闭的分组（有任意一个即算） */
    const hasHiddenGroupsForDevice = (deviceId) =>
      [...hiddenGroupKeys.value].some((k) => k.startsWith(`${deviceId}-`))
    const getVisibleGroups = (deviceData) => {
      const groups = getSensorGroups(deviceData.sensors).groups
      return groups.filter((g) => !isGroupHidden(deviceData.device.id, g))
    }

    // 判断是否为继电器/开关类型（需要在 fetchDevicesWithSensors 之前定义）
    const isRelayType = (type) => {
      if (!type) return false
      const t = type.toLowerCase()
      return t.includes('relay') || t.includes('开关') || t.includes('switch')
    }

    // 获取所有主题配置
    const fetchAllTopicConfigs = async () => {
      try {
        const response = await axios.get('/api/topic-configs')
        allTopicConfigs.value = response.data || []
      } catch (error) {
        console.error('获取主题配置失败:', error)
      }
    }
    
    // 根据设备的 topic_config_id 获取对应的主题配置
    const getDeviceTopicConfig = (device) => {
      if (!device.topic_config_id) return null
      return allTopicConfigs.value.find(c => c.id === device.topic_config_id)
    }

    // 从EMQX获取客户端连接状态
    const fetchClientStatus = async () => {
      try {
        const response = await axios.get('/api/mqtt-publish/clients')
        const clientsData = response.data
        const onlineClientIds = new Set()
        
        if (clientsData && clientsData.data) {
          clientsData.data.forEach(client => {
            if (client.connected) {
              onlineClientIds.add(client.clientid)
            }
          })
        }
        
        return onlineClientIds
      } catch (error) {
        console.error('获取客户端状态失败:', error)
        return new Set()
      }
    }

    const fetchDevices = async () => {
      try {
        isLoading.value = true
        const response = await axios.get('/api/devices')
        devices.value = response.data
      } catch (error) { console.error(error) } finally { isLoading.value = false }
    }

    const fetchDevicesWithSensors = async () => {
      try {
        await fetchDevices()
        
        // 获取EMQX客户端连接状态
        const onlineClientIds = await fetchClientStatus()
        
        const sensorsResponse = await axios.get('/api/sensors/latest')
        const allSensors = sensorsResponse.data || []
        const sensorMap = new Map()
        allSensors.forEach(s => {
          if (!sensorMap.has(s.device_id)) sensorMap.set(s.device_id, [])
          sensorMap.get(s.device_id).push(s)
        })
        
        // 保存旧的传感器数据，以便保留 display_name
        const oldDevicesMap = new Map()
        devicesWithSensors.value.forEach(d => {
          const sensorMap = new Map()
          d.sensors.forEach(s => {
            sensorMap.set(s.type, s)
          })
          oldDevicesMap.set(d.device.id, sensorMap)
        })
        
        devicesWithSensors.value = devices.value
          .filter(d => d.show_on_dashboard !== false)
          .map(device => {
            const sensors = sensorMap.get(device.id) || []
            const sensorTypeMap = new Map()
            const oldSensors = oldDevicesMap.get(device.id)
            
            sensors.forEach(sensor => {
              if (!sensorTypeMap.has(sensor.type) || new Date(sensor.timestamp) > new Date(sensorTypeMap.get(sensor.type).timestamp)) {
                // 保留旧的 display_name（如果存在）
                if (oldSensors && oldSensors.has(sensor.type)) {
                  const oldSensor = oldSensors.get(sensor.type)
                  if (oldSensor.display_name !== undefined) {
                    sensor.display_name = oldSensor.display_name
                  }
                }
                
                if (isRelayType(sensor.type)) {
                  const key = `${device.id}-${sensor.type}`
                  const exp = relayExpectedStates.value.get(key)
                  if (exp && (Date.now() - exp.timestamp < exp.timeout)) {
                    if (sensor.value === exp.value) relayExpectedStates.value.delete(key)
                    else sensor.value = exp.value
                  }
                }
                sensorTypeMap.set(sensor.type, sensor)
              }
            })
            
            // 判断设备在线状态：优先使用 clientid，其次使用 name，最后使用 id
            let isOnline = false
            if (device.clientid) {
              // 如果设备有明确的 clientid，使用它来判断
              isOnline = onlineClientIds.has(device.clientid)
            } else if (device.name) {
              // 否则尝试使用 name
              isOnline = onlineClientIds.has(device.name)
            } else {
              // 最后尝试使用 id（转换为字符串）
              isOnline = onlineClientIds.has(String(device.id))
            }
            
            return { device, sensors: Array.from(sensorTypeMap.values()), isOnline }
          })
        handleSearch()
      } catch (e) { console.error(e) }
    }

    const handleSearch = () => {
      const keyword = searchKeyword.value.trim().toLowerCase()
      if (!keyword) { filteredDevices.value = devicesWithSensors.value; return }
      filteredDevices.value = devicesWithSensors.value.filter(d => 
        (d.device.name || '').toLowerCase().includes(keyword) || 
        (d.device.display_name || '').toLowerCase().includes(keyword) ||
        (d.device.location || '').toLowerCase().includes(keyword)
      )
    }

    const clearSearch = () => { searchKeyword.value = ''; filteredDevices.value = devicesWithSensors.value }
    const formatSensorValue = (v) => typeof v === 'number' ? v.toFixed(1) : v
    
    // 改良后的识别逻辑：不区分大小写
    const isPrioritySensor = (type) => {
      if (!type) return false
      const t = type.toLowerCase()
      return (t.includes('temp') || t.includes('hum')) && !t.includes('relay')
    }

    const getPrioritySensors = (sensors) => {
      return sensors.filter(s => isPrioritySensor(s.type)).sort((a, b) => {
        const at = a.type.toLowerCase(), bt = b.type.toLowerCase()
        if (at.includes('temp') && bt.includes('hum')) return -1
        if (at.includes('hum') && bt.includes('temp')) return 1
        return a.type.localeCompare(b.type)
      })
    }

    // 提取传感器类型中的编号
    // air_temperature_1 -> { type: 'air', num: 1 }
    // comp1_in_temperature_F -> { type: 'comp', num: 1 }
    const parseSensorType = (type) => {
      if (!type) return null
      
      // 匹配环境传感器 (air_temperature_1)
      const airMatch = type.match(/air_.*_([0-9]+)$/)
      if (airMatch) return { groupType: 'air', num: airMatch[1] }

      // 匹配压缩机传感器 (comp1_in_...)
      const compMatch = type.match(/comp([0-9]+)_.*_temperature/)
      if (compMatch) return { groupType: 'comp', num: compMatch[1] }
      
      return null
    }

    // 将温湿度传感器按编号分组
    const getSensorGroups = (sensors) => {
      const prioritySensors = getPrioritySensors(sensors)
      const groupMap = new Map() // Key: "type-num"
      const ungrouped = []

      // 所有的传感器过一遍，尝试分组
      sensors.forEach(sensor => { // 注意：这里使用 sensors 而不是 prioritySensors，以免漏掉 comp 类型的（如果不包含在 priority 中）
        if (isReadOnlyRelayInput(sensor.type)) return // 跳过只读继电器

        const parsed = parseSensorType(sensor.type)
        const type = sensor.type.toLowerCase()
         // 只处理我们关心的几种类型：air temp/hum, comp in/out
        const isTarget = isPrioritySensor(sensor.type) || type.includes('comp')

        if (parsed && isTarget) {
          const key = `${parsed.groupType}-${parsed.num}`
          if (!groupMap.has(key)) {
            groupMap.set(key, { 
              groupType: parsed.groupType, 
              number: parsed.num, 
              // air props
              temp: null, 
              hum: null,
              // comp props
              in: null,
              out: null
            })
          }
          
          const group = groupMap.get(key)
          
          if (parsed.groupType === 'air') {
             if (type.includes('temp')) group.temp = sensor
             else if (type.includes('hum')) group.hum = sensor
          } else if (parsed.groupType === 'comp') {
             if (type.includes('in')) group.in = sensor
             else if (type.includes('out')) group.out = sensor
          }
        } else if (isTarget) {
          // 是目标类型（如Priority）但没解析出编号，或者是单个的
          ungrouped.push(sensor)
        }
      })
      
      // 过滤掉不完整的组（可选，这里我们全部显示，单腿也显示）
      const groupArray = Array.from(groupMap.values()).sort((a, b) => {
        if (a.groupType !== b.groupType) return a.groupType.localeCompare(b.groupType)
        return parseInt(a.number) - parseInt(b.number)
      })

      // 还需要把那些根本不在 priority 和 comp 规则里的传感器找出来（getOtherSensors 负责）
      // 这里只需要返回我们不仅处理了 priority，还处理了 comp 的结果
      
      // 注意：上面的逻辑由于使用了 sensors 全集，可能会把 priorityLogic 里的也包含进去。
      // 为了不破坏原有逻辑，我们还是只处理 Priority 里的 + Comp 里的。
      // 既然用户需求是要把这些分组，那展示的时候优先展示分组。
      
      return { groups: groupArray, ungrouped }
    }
    
    // 覆盖原有的 hasPrioritySensors 逻辑，如果分组里有东西也通过
    const hasGroupsOrPriority = (sensors) => {
        const { groups, ungrouped } = getSensorGroups(sensors)
        return groups.length > 0 || ungrouped.length > 0
    }

    // 判断是否为只读的继电器输入类型（不应该在列表中显示控制按钮）
    const isReadOnlyRelayInput = (type) => {
      if (!type) return false
      const t = type.toLowerCase()
      return t === 'realy_in_status' || t === 'relay_in_status'
    }
    
    const getOtherSensors = (sensors) => sensors.filter(s => !isPrioritySensor(s.type) && !isReadOnlyRelayInput(s.type))
    const hasPrioritySensors = (sensors) => sensors && sensors.some(s => isPrioritySensor(s.type))
    const getDeviceDisplayName = (d) => (d.display_name && d.display_name.trim()) ? d.display_name.trim() : d.name
    
    // 获取 realy_in_status 传感器的值（始终返回数字，默认为0）
    // 只取 realy_in_status（实时上报，时效性高），不取 relay_in_status（10秒上报，时效性低）
    const getRelayInStatusValue = (sensors) => {
      if (!sensors) return 0
      // 只查找 realy_in_status（实时数据）
      const sensor = sensors.find(s => s.type === 'realy_in_status')
      return sensor ? (sensor.value || 0) : 0
    }
    
    // 获取继电器输入的显示名称（从 device.relay_in_display_name 读取）
    const getRelayInDisplayName = (device) => {
      if (!device) return '继电器输入'
      return (device.relay_in_display_name && device.relay_in_display_name.trim()) 
        ? device.relay_in_display_name.trim() 
        : '继电器输入'
    }
    
    // 开始编辑继电器输入名称
    const startEditRelayIn = (device) => {
      editingRelayInId.value = device.id
      editingRelayInName.value = getRelayInDisplayName(device)
    }
    
    // 保存继电器输入名称
    const saveRelayInName = async (deviceId) => {
      try {
        const name = editingRelayInName.value.trim()
        await axios.put(`/api/devices/${deviceId}/relay-in-display-name`, { 
          relay_in_display_name: name || null 
        })
        
        // 更新本地数据
        const deviceData = devicesWithSensors.value.find(x => x.device.id === deviceId)
        if (deviceData) {
          deviceData.device.relay_in_display_name = name || null
        }
        
        cancelEditRelayIn()
      } catch (e) {
        console.error('保存继电器输入名称失败:', e)
        alert('保存失败: ' + (e.response?.data?.detail || e.message))
      }
    }
    
    // 取消编辑继电器输入名称
    const cancelEditRelayIn = () => {
      editingRelayInId.value = null
      editingRelayInName.value = ''
    }
    
    const getSensorDisplayName = (s) => {
      if (s.display_name && s.display_name.trim()) return s.display_name.trim()
      return typeof s === 'string' ? s : s.type
    }

    const startEditDevice = (d) => {
      editingDeviceId.value = d.id; editingDeviceName.value = getDeviceDisplayName(d)
      setTimeout(() => { const i = document.querySelector(`input[data-device-id="${d.id}"]`); i?.focus(); i?.select() }, 100)
    }

    const saveDeviceName = async (id) => {
      try {
        const name = editingDeviceName.value.trim()
        await axios.put(`/api/devices/${id}/display-name`, { display_name: name || null })
        const d = devicesWithSensors.value.find(x => x.device.id === id)
        if (d) d.device.display_name = name || null
        cancelEditDevice()
      } catch (e) { alert('保存失败') }
    }

    const cancelEditDevice = () => { editingDeviceId.value = null; editingDeviceName.value = '' }

    const startEditSensor = (id, s) => {
      const key = `${id}-${s.type}`
      editingSensorId.value = key; editingSensorName.value = getSensorDisplayName(s)
      setTimeout(() => { const i = document.querySelector(`input[data-sensor-key="${key}"]`); i?.focus(); i?.select() }, 100)
    }

    const saveSensorName = async (deviceId, sensor) => {
      try {
        const name = editingSensorName.value.trim()
        await axios.put(`/api/sensors/device/${deviceId}/type/${encodeURIComponent(sensor.type)}/display-name`, { display_name: name || null })
        const d = devicesWithSensors.value.find(x => x.device.id === deviceId)
        if (d) { const s = d.sensors.find(x => x.type === sensor.type); if (s) s.display_name = name || null }
        cancelEditSensor()
      } catch (e) { alert('保存失败') }
    }

    const cancelEditSensor = () => { editingSensorId.value = null; editingSensorName.value = '' }

    const isRelaySending = (id, type) => {
      const key = `${id}-${type}`
      return sendingRelayId.value === key || relayToggleLock.value.has(key)
    }

    const toggleRelay = async (device, sensor) => {
      const key = `${device.id}-${sensor.type}`
      if (isRelaySending(device.id, sensor.type)) return
      
      // 获取设备关联的主题配置
      const deviceTopicConfig = getDeviceTopicConfig(device)
      
      // 方案A：设备必须通过 topic_config_id 关联主题配置，并且主题配置中必须配置继电器格式
      if (!deviceTopicConfig) {
        alert(`设备 ${device.name} 未关联主题配置，无法控制继电器！\n请在设备编辑页面关联主题配置。`)
        return
      }
      
      if (!deviceTopicConfig.relay_on_payload || !deviceTopicConfig.relay_off_payload) {
        alert(`设备 ${device.name} 关联的主题配置未设置继电器控制格式！\n请在主题配置页面设置继电器开启/关闭消息格式。`)
        return
      }
      
      sendingRelayId.value = key; relayToggleLock.value.add(key)
      try {
        const topic = device.publish_topic || `pc/${device.id}`
        
        // 只使用主题配置中的继电器格式（一对一关系）
        const msg = sensor.value > 0 
          ? deviceTopicConfig.relay_off_payload  // 关闭继电器
          : deviceTopicConfig.relay_on_payload   // 开启继电器
        
        const res = await axios.post('/api/mqtt-publish/publish', { topic, message: msg })
        if (res.data.success) {
          const val = sensor.value > 0 ? 0 : 1
          relayExpectedStates.value.set(key, { value: val, timestamp: Date.now(), timeout: 5000 })
          sensor.value = val
        }
      } catch (e) { alert('发送失败') } finally { sendingRelayId.value = null; relayToggleLock.value.delete(key) }
    }

    const getSensorPercentage = (s) => {
      if (s.min_value === null || s.max_value === null) return 0
      return Math.min(100, Math.max(0, ((s.value - s.min_value) / (s.max_value - s.min_value)) * 100))
    }

    const getSensorStatusClass = (s) => {
      const t = s.type.toLowerCase()
      if (t.includes('temp')) {
        if (s.value > 30) return 'bg-danger'
        if (s.value > 28) return 'bg-warning'
        return 'bg-success'
      } else if (t.includes('hum')) {
        if (s.value > 70) return 'bg-danger'
        if (s.value > 65) return 'bg-warning'
        return 'bg-success'
      }
      return 'bg-primary'
    }

    const formatShortDate = (d) => d ? new Date(d).toLocaleDateString('zh-CN') : ''

    // STM32_4 设备的温度监控
    const stm32Device = computed(() => {
      return devicesWithSensors.value.find(d => 
        d.device.name === 'stm32_4' || 
        (d.device.display_name && d.device.display_name.toLowerCase().includes('stm32_4'))
      )
    })
    
    // 获取压缩机温度值
    const getCompressorTemp = (compressorNum, type) => {
      if (!stm32Device.value) return '--'
      const sensorType = `comp${compressorNum}_${type}_temperature_F`
      const sensor = stm32Device.value.sensors.find(s => s.type === sensorType)
      if (!sensor || sensor.value === null || sensor.value === undefined) return '--'
      return formatSensorValue(sensor.value)
    }
    
    // 判断压缩机是否正常运行（出口温度应该 >= 入口温度）
    const isCompressorNormal = (compressorNum) => {
      if (!stm32Device.value) return false
      
      const inSensorType = `comp${compressorNum}_in_temperature_F`
      const outSensorType = `comp${compressorNum}_out_temperature_F`
      
      const inSensor = stm32Device.value.sensors.find(s => s.type === inSensorType)
      const outSensor = stm32Device.value.sensors.find(s => s.type === outSensorType)
      
      // 如果任一传感器数据缺失，视为异常
      if (!inSensor || !outSensor || 
          inSensor.value === null || inSensor.value === undefined ||
          outSensor.value === null || outSensor.value === undefined) {
        return false
      }
      
      // 正常：出口温度 >= 入口温度
      // 异常：出口温度 < 入口温度
      return outSensor.value >= inSensor.value
    }
    
    const getCompressorGroupClass = (compressorNum) => {
      return isCompressorNormal(compressorNum) ? 'compressor-normal' : 'compressor-abnormal'
    }

    onMounted(async () => {
      await fetchAllTopicConfigs()
      await fetchDevicesWithSensors()
      refreshInterval = setInterval(fetchDevicesWithSensors, 2000)
    })
    onUnmounted(() => { if (refreshInterval) clearInterval(refreshInterval) })

    return {
      devices, devicesWithSensors, filteredDevices, isLoading, searchKeyword, authStore,
      stm32Device, getCompressorTemp, isCompressorNormal, getCompressorGroupClass,
      editingSensorId, editingSensorName, editingDeviceId, editingDeviceName, 
      editingRelayInId, editingRelayInName, sendingRelayId,
      onlineDevices: computed(() => devicesWithSensors.value.filter(d => d.isOnline).length),
      offlineDevices: computed(() => devicesWithSensors.value.filter(d => !d.isOnline).length),
      formatSensorValue, getDeviceDisplayName, getSensorDisplayName, getSensorPercentage,
      getSensorStatusClass, formatShortDate, getPrioritySensors, getSensorGroups, hasGroupsOrPriority, getOtherSensors, hasPrioritySensors,
      handleSearch, clearSearch, startEditDevice, saveDeviceName, cancelEditDevice,
      startEditSensor, saveSensorName, cancelEditSensor, toggleRelay, isRelaySending, isRelayType,
      getRelayInStatusValue, getRelayInDisplayName, startEditRelayIn, saveRelayInName, 
      cancelEditRelayIn, isReadOnlyRelayInput,
      hideGroup, restoreGroups, hasHiddenGroupsForDevice, getVisibleGroups, hoveredDeviceIdForRestore
    }
  }
}
</script>

<style scoped>
/* 统计卡片样式 */
.stats-container { margin: 0 -15px 30px -15px; padding: 0 15px; }
.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  border: 2px solid transparent;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.stat-card-total { border-color: #667eea; }
.stat-card-online { border-color: #10b981; }
.stat-card-offline { border-color: #ef4444; }

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}
.stat-card-total .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}
.stat-card-online .stat-icon {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}
.stat-card-offline .stat-icon {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.stat-content {
  flex: 1;
}
.stat-value {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
}
.stat-card-total .stat-value { color: #667eea; }
.stat-card-online .stat-value { color: #10b981; }
.stat-card-offline .stat-value { color: #ef4444; }

.stat-label {
  font-size: 0.9rem;
  color: #6c757d;
  font-weight: 500;
}

/* 状态指示器样式 */
.status-indicator {
  font-size: 0.65rem;
  display: inline-flex;
  align-items: center;
}
.status-online {
  color: #10b981;
  animation: pulse 2s ease-in-out infinite;
}
.status-offline {
  color: #ef4444;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.device-card { 
  transition: transform 0.2s, box-shadow 0.2s; 
  border: 1px solid #dee2e6; 
  display: flex;
  flex-direction: column;
}
.device-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important; }
.device-card .card-body {
  flex-grow: 1;
  min-height: 150px;
}
.card-header { background-color: #f8f9fa; border-bottom: 1px solid #dee2e6; }
.device-name { font-size: 0.95rem; font-weight: 600; color: #212529; }
.device-name-text {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
  vertical-align: middle;
}
.device-icon { opacity: 0.6; }
.device-location-wrapper {
  display: block;
  width: 100%;
}
.device-location {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
  vertical-align: middle;
}
.priority-metrics-container {
  position: relative;
}
.priority-metrics { 
  background: linear-gradient(135deg, #f0f7ff 0%, #ffffff 100%); 
  border-radius: 6px; 
  padding: 4px; 
  border: 1px solid #e3f2fd; 
}
.restore-button-wrapper {
  position: absolute;
  top: -8px;
  right: 8px;
  z-index: 10;
  background: white;
  border-radius: 4px;
  padding: 2px 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.metric-card { background: white; border-radius: 4px; padding: 8px; border-left: 3px solid #2196F3; }

/* 美观的 Mini 分组卡片 (复刻 Compressor Group 风格) */
.mini-group-card {
  background: white;
  border-radius: 8px;
  padding: 8px 12px;
  border: 1px solid #e5e7eb; /* 默认灰色边框 */
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  transition: all 0.2s;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.mini-group-card:hover {
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  transform: translateY(-1px);
}

/* 状态边框色 */
.mini-group-card.status-normal { border-left: 3px solid #10b981; }
.mini-group-card.status-abnormal { border-left: 3px solid #ef4444; }
.mini-group-card.status-default { border-left: 3px solid #3b82f6; } /* 蓝色默认 */

.mini-group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  border-bottom: 1px solid #f3f4f6;
  padding-bottom: 4px;
}

.mini-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-group-close {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 2px 6px;
  font-size: 0.9rem;
  line-height: 1;
  border-radius: 4px;
  transition: color 0.2s, background 0.2s;
}
.btn-group-close:hover {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.btn-restore-subtle {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 2px 8px;
  font-size: 0.8rem;
  line-height: 1.2;
  border-radius: 4px;
  transition: color 0.2s;
}
.btn-restore-subtle:hover {
  color: #6b7280;
}

.mini-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 1;
}

/* 传感器项样式 */
.mini-sensor-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative; /* 用于放置编辑按钮 */
}

/* 编辑按钮 (显式但小巧) */
.mini-edit-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #9ca3af;
  font-size: 0.7rem;
  padding: 0 4px;
  margin-left: 2px;
  opacity: 0.5;
  transition: opacity 0.2s;
  vertical-align: middle;
}
.mini-edit-btn:hover { opacity: 1; color: #3b82f6; }

.mini-label-container {
  min-height: 18px; /* 保证高度防止抖动 */
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.mini-label {
  font-size: 0.7rem;
  color: #9ca3af;
  margin-bottom: 2px;
  display: flex;
  align-items: center;
  max-width: 80px; /* 限制标签最大宽度 */
}

/* Mini 编辑框样式 */
.mini-edit-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  width: 100%;
  margin-bottom: 2px;
}

.mini-input {
  font-size: 0.7rem;
  padding: 0 4px;
  height: 20px;
  width: 70px; /* 小巧宽度 */
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.btn-mini-action {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0 2px;
  font-size: 0.75rem;
  line-height: 1;
  display: flex;
  align-items: center;
}
.btn-mini-action:hover { opacity: 0.8; }

.mini-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: #374151;
  line-height: 1.2;
}
.mini-value .unit { font-size: 0.75rem; font-weight: 400; color: #9ca3af; margin-left: 1px; }

/* 状态色文字 */
.text-success { color: #10b981 !important; }
.text-danger { color: #ef4444 !important; }

/* 流程箭头 */
.flow-arrow {
  color: #d1d5db;
  font-size: 0.9rem;
  margin: 0 8px;
}
.metric-label { 
  font-size: 0.75rem; 
  color: #6c757d; 
  margin-bottom: 4px; 
  font-weight: 500; 
  display: flex; 
  align-items: center; 
  gap: 4px;
  min-height: 20px;
}
.metric-value { 
  font-size: 1.3rem; 
  font-weight: 700; 
  color: #2196F3; 
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.metric-unit { font-size: 0.8rem; color: #6c757d; font-weight: 400; }
.metric-bar { height: 4px; background-color: #e9ecef; border-radius: 2px; margin-top: 6px; overflow: hidden; }
.metric-progress { height: 100%; border-radius: 2px; transition: width 0.3s ease; }
.other-sensors { margin-top: 8px; }
.sensor-row { padding: 4px 0; border-bottom: 1px solid #f0f0f0; }
.sensor-row-content {
  flex-wrap: wrap;
  gap: 8px;
}
.sensor-label { 
  font-size: 0.8rem; 
  color: #6c757d; 
  display: flex; 
  align-items: center; 
  gap: 4px;
  flex: 1;
  min-width: 0;
}
.sensor-label-text {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
  vertical-align: middle;
}
.sensor-name-wrapper, .device-name-wrapper { 
  display: inline-flex; 
  align-items: center; 
  gap: 4px; 
  cursor: default;
  min-width: 0;
  max-width: 100%;
}
.sensor-value-actions {
  flex-shrink: 0;
  flex-wrap: wrap;
}
.btn-edit-sensor, .btn-edit-device { background: transparent; border: none; color: #6c757d; padding: 2px 6px; cursor: pointer; opacity: 0.3; font-size: 0.7rem; border-radius: 3px; }
.sensor-name-wrapper:hover .btn-edit-sensor, .device-name-wrapper:hover .btn-edit-device, .device-card:hover .btn-edit-device { opacity: 1; }
.btn-edit-sensor:hover, .btn-edit-device:hover { color: #007bff; background: rgba(0, 123, 255, 0.15); }
.sensor-edit-input, .device-edit-input { display: flex; align-items: center; gap: 4px; width: 100%; }
.relay-toggle-btn { 
  padding: 2px 8px; 
  font-size: 0.7rem; 
  min-width: 60px;
  white-space: nowrap;
}
.sensor-value-small { 
  font-size: 0.85rem; 
  font-weight: 600; 
  color: #495057;
  white-space: nowrap;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.device-info { 
  font-size: 0.75rem;
  overflow: hidden;
}
.device-info span {
  display: inline-block;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: middle;
}
.search-container { margin: 0 -15px 20px -15px; padding: 0 15px; }
.search-box { max-width: 600px; margin: 0 auto; }
.search-input-wrapper { position: relative; display: flex; align-items: center; background: #ffffff; border: 2px solid #e9ecef; border-radius: 12px; padding: 0 16px; }
.search-input { flex: 1; border: none; outline: none; padding: 12px 8px; font-size: 1rem; }
.header-banner { margin: -15px -15px 30px -15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.banner-container { height: 200px; display: flex; align-items: center; justify-content: center; position: relative; }
.banner-image { max-height: 100%; object-fit: contain; }
.banner-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.2); display: flex; align-items: center; justify-content: center; color: white; }

/* 响应式改进 */
@media (max-width: 768px) {
  .device-name-text {
    max-width: 140px;
  }
  
  .sensor-label-text {
    max-width: 100px;
  }
  
  .sensor-row-content {
    flex-direction: column;
    align-items: flex-start !important;
  }
  
  .sensor-value-actions {
    width: 100%;
    justify-content: flex-start;
    margin-top: 4px;
  }
  
  .relay-toggle-btn {
    margin-top: 4px;
  }
  
  .device-info span {
    max-width: 100px;
  }
}

@media (max-width: 576px) {
  .device-name-text {
    max-width: 120px;
  }
  
  .sensor-label-text {
    max-width: 80px;
  }
  
  .stat-card {
    padding: 15px;
  }
  
  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 24px;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
  
  .banner-container {
    height: 150px;
  }
}

/* 改进卡片视觉一致性 */
.metric-card {
  min-height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* 改进搜索框在小屏幕的显示 */
@media (max-width: 576px) {
  .search-input {
    font-size: 0.9rem;
    padding: 10px 6px;
  }
  
  .search-input-wrapper {
    padding: 0 12px;
  }
}

/* 提升 tooltip 体验 */
[title] {
  cursor: help;
}

.device-name-text[title],
.sensor-label-text[title],
.device-location[title] {
  cursor: default;
}

/* 继电器输入状态指示器样式（只读，显示外部输入状态） */
.device-icon-area {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.relay-in-status-indicator {
  text-align: right;
}

.relay-in-status-indicator .relay-label-wrapper {
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  min-height: 20px;
}

.relay-in-status-indicator .status-label {
  font-size: 0.7rem;
  color: #6c757d;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}

.relay-in-name-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.btn-edit-relay-in {
  background: transparent;
  border: none;
  color: #6c757d;
  padding: 2px 6px;
  cursor: pointer;
  opacity: 0.3;
  font-size: 0.7rem;
  border-radius: 3px;
  transition: opacity 0.2s;
}

.relay-in-status-indicator:hover .btn-edit-relay-in,
.relay-in-name-wrapper:hover .btn-edit-relay-in {
  opacity: 1;
}

.btn-edit-relay-in:hover {
  color: #007bff;
  background: rgba(0, 123, 255, 0.15);
}

.relay-in-edit-input {
  display: flex;
  align-items: center;
  gap: 2px;
}

.relay-in-edit-input input {
  font-size: 0.7rem;
  padding: 2px 6px;
  width: 100px;
  height: 24px;
}

.relay-in-edit-input .btn {
  padding: 2px 6px;
  font-size: 0.65rem;
  height: 24px;
  line-height: 1;
}

.relay-in-status-indicator .status-icon {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
}

.relay-in-status-indicator .status-icon.status-on {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.relay-in-status-indicator .status-icon.status-off {
  background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
  color: white;
}

.relay-in-status-indicator .status-text {
  font-size: 0.75rem;
  font-weight: 700;
}

/* 改进编辑输入框的响应式 */
@media (max-width: 768px) {
  .sensor-edit-input input,
  .device-edit-input input {
    max-width: 150px;
  }
}

/* STM32_4 温度监控专区样式 */
.temperature-monitor-card {
  border: 2px solid #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.bg-gradient-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 压缩机组件样式 */
.compressor-group {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 3px solid transparent;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.compressor-group.compressor-normal {
  border-color: #10b981;
  background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
}

.compressor-group.compressor-abnormal {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);
  animation: compressorPulse 2s ease-in-out infinite;
}

@keyframes compressorPulse {
  0%, 100% { 
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
  }
  50% { 
    box-shadow: 0 4px 16px rgba(239, 68, 68, 0.6);
  }
}

.compressor-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e5e7eb;
}

.compressor-icon-wrapper {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  flex-shrink: 0;
}

.compressor-fan-icon {
  font-size: 32px;
  color: white;
  transition: all 0.3s ease;
}

.fan-rotating {
  animation: fanRotate 2s linear infinite;
}

@keyframes fanRotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.compressor-group.compressor-abnormal .compressor-fan-icon {
  animation: none !important;
  color: #fca5a5;
}

.compressor-group.compressor-abnormal .compressor-icon-wrapper {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.compressor-title {
  flex: 1;
  font-size: 1.2rem;
  font-weight: 700;
  color: #374151;
  margin: 0;
}

/* 温度对显示 */
.temperature-pair {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 0;
}

.temp-item {
  flex: 1;
  text-align: center;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
  padding: 16px;
}

.temp-item-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.temp-item-value {
  font-size: 2.2rem;
  font-weight: 700;
  color: #10b981;
  line-height: 1;
  transition: color 0.3s ease;
}

.temp-item-value.temp-danger {
  color: #ef4444;
  animation: tempValuePulse 1.5s ease-in-out infinite;
}

@keyframes tempValuePulse {
  0%, 100% { 
    opacity: 1;
  }
  50% { 
    opacity: 0.7;
  }
}

.temp-unit {
  font-size: 1rem;
  font-weight: 500;
  color: #6b7280;
  margin-left: 4px;
}

.temp-arrow {
  font-size: 2rem;
  color: #667eea;
  flex-shrink: 0;
}

.compressor-group.compressor-abnormal .temp-arrow {
  color: #ef4444;
}

.compressor-status {
  text-align: center;
  margin-top: auto;
}

.compressor-status .badge {
  padding: 8px 20px;
  font-size: 0.9rem;
  font-weight: 600;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .compressor-group {
    padding: 20px;
  }
  
  .compressor-icon-wrapper {
    width: 50px;
    height: 50px;
  }
  
  .compressor-fan-icon {
    font-size: 26px;
  }
  
  .compressor-title {
    font-size: 1rem;
  }
  
  .temperature-pair {
    flex-direction: column;
    gap: 12px;
  }
  
  .temp-arrow {
    transform: rotate(90deg);
    font-size: 1.5rem;
  }
  
  .temp-item-value {
    font-size: 1.8rem;
  }
}

@media (max-width: 576px) {
  .compressor-group {
    padding: 16px;
  }
  
  .compressor-header {
    gap: 12px;
  }
  
  .compressor-icon-wrapper {
    width: 45px;
    height: 45px;
  }
  
  .compressor-fan-icon {
    font-size: 22px;
  }
  
  .compressor-title {
    font-size: 0.95rem;
  }
  
  .temp-item {
    padding: 12px;
  }
  
  .temp-item-value {
    font-size: 1.6rem;
  }
  
  .temp-item-label {
    font-size: 0.75rem;
  }
}
</style>
