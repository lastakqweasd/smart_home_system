<template>
  <div class="create-scene">
    <header class="header">
      <router-link 
        :to="step > 1 ? '#' : '/'" 
        class="back-btn"
        @click="handleBack"
      >
        <i class="fas fa-arrow-left"></i> {{ step > 1 ? '上一步' : '返回' }}
      </router-link>
      <h1 class="header__title">创建场景模式</h1>
      <div class="header__steps">
        <span :class="{ active: step >= 1 }">1</span>
        <span :class="{ active: step >= 2 }">2</span>
        <span :class="{ active: step >= 3 }">3</span>
      </div>
    </header>
    
    <div class="form-container">
      <!-- 第一步：基本信息 -->
      <transition name="fade" mode="out-in">
        <div class="form-section" v-if="step === 1" key="step1">
          <h2 class="section-title">
            <i class="fas fa-info-circle"></i> 场景基本信息
          </h2>
          
          <div class="form-group">
            <label for="scene-name">
              <i class="fas fa-tag"></i> 场景名称
            </label>
            <input 
              id="scene-name" 
              v-model="scene.name" 
              type="text" 
              placeholder="例如：回家模式、睡眠模式"
              maxlength="20"
            >
            <div class="char-counter">{{ scene.name.length }}/20</div>
          </div>
          
          <div class="form-group">
            <label for="scene-description">
              <i class="fas fa-align-left"></i> 场景描述
            </label>
            <textarea 
              id="scene-description" 
              v-model="scene.description" 
              placeholder="描述此场景的功能和效果"
              maxlength="100"
            ></textarea>
            <div class="char-counter">{{ scene.description.length }}/100</div>
          </div>
          
          <div class="form-group">
            <label><i class="fas fa-icons"></i> 场景图标</label>
            <div class="icon-grid">
              <div 
                v-for="icon in sceneIcons" 
                :key="icon.id"
                class="icon-card"
                :class="{ selected: scene.icon === icon.id }"
                @click="scene.icon = icon.id"
              >
                <div class="icon-wrapper" :class="icon.id">
                  <i :class="icon.class"></i>
                </div>
                <span>{{ icon.label }}</span>
              </div>
            </div>
          </div>
          
          <button 
            class="next-btn"
            :disabled="!scene.name.trim()"
            @click="step = 2"
          >
            下一步 <i class="fas fa-arrow-right"></i>
          </button>
        </div>
      </transition>
      
      <!-- 第二步：选择设备 -->
      <transition name="fade" mode="out-in">
        <div class="form-section" v-if="step === 2" key="step2">
          <h2 class="section-title">
            <i class="fas fa-microchip"></i> 选择场景设备
          </h2>
          
          <div class="search-filter">
            <div class="search-box">
              <i class="fas fa-search"></i>
              <input 
                type="text" 
                v-model="deviceSearch" 
                placeholder="搜索设备..."
              >
            </div>
            
            <div class="room-filters">
              <button 
                class="filter-btn"
                :class="{ active: selectedRoom === 'all' }"
                @click="selectedRoom = 'all'"
              >
                全部设备
              </button>
              <button 
                v-for="room in rooms" 
                :key="room.id"
                class="filter-btn"
                :class="{ active: selectedRoom === room.name }"
                @click="selectedRoom = room.name"
              >
                {{ room.name }}
              </button>
            </div>
          </div>
          
          <div v-if="filteredDevices.length === 0" class="no-devices">
            <i class="fas fa-plug"></i>
            <p>没有找到匹配的设备</p>
          </div>
          
          <div v-else class="device-list">
            <div 
              v-for="device in filteredDevices" 
              :key="device.id"
              class="device-item"
              :class="{ selected: isDeviceSelected(device.id) }"
            >
              <div class="device-info" @click="toggleDeviceSelection(device.id)">
                <div class="device-icon" :style="{ backgroundColor: getDeviceColor(device.type) }">
                  <i :class="getDeviceIcon(device.type)"></i>
                </div>
                <div class="device-details">
                  <h3>{{ device.name }}</h3>
                  <p>{{ device.room }} · {{ device.type }}</p>
                </div>
                <div class="device-check">
                  <i class="fas fa-check"></i>
                </div>
              </div>
              
              <div v-if="isDeviceSelected(device.id)" class="device-controls">
                <div class="control-group">
                  <label>开关状态</label>
                  <div class="toggle-switch">
                    <input 
                      type="checkbox" 
                      :id="'power-' + device.id" 
                      v-model="deviceStates[device.id].status"
                    >
                    <label :for="'power-' + device.id"></label>
                  </div>
                </div>
                
                <div v-if="device.type === 'light'" class="control-group">
                  <label>亮度</label>
                  <input 
                    type="range" 
                    min="0" 
                    max="100" 
                    v-model="deviceStates[device.id].brightness"
                    :disabled="!deviceStates[device.id].status"
                  >
                  <span>{{ deviceStates[device.id].brightness }}%</span>
                </div>
                
                <div v-if="device.type === 'ac'" class="control-group">
                  <label>温度</label>
                  <input 
                    type="range" 
                    min="16" 
                    max="30" 
                    v-model="deviceStates[device.id].temperature"
                    :disabled="!deviceStates[device.id].status"
                  >
                  <span>{{ deviceStates[device.id].temperature }}°C</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <button class="back-btn" @click="step = 1">
              <i class="fas fa-arrow-left"></i> 上一步
            </button>
            <button 
              class="next-btn"
              :disabled="selectedDeviceCount === 0"
              @click="step = 3"
            >
              下一步 <i class="fas fa-arrow-right"></i>
            </button>
          </div>
        </div>
      </transition>
      
      <!-- 第三步：确认设置 -->
      <transition name="fade" mode="out-in">
        <div class="form-section" v-if="step === 3" key="step3">
          <h2 class="section-title">
            <i class="fas fa-check-circle"></i> 确认场景设置
          </h2>
          
          <div class="scene-summary">
            <div class="scene-header">
              <div class="scene-icon" :class="scene.icon">
                <i :class="getSceneIcon(scene.icon)"></i>
              </div>
              <div class="scene-details">
                <h3>{{ scene.name }}</h3>
                <p>{{ scene.description || '无描述' }}</p>
              </div>
            </div>
            
            <div class="selected-devices">
              <h4>包含设备 ({{ selectedDeviceCount }})</h4>
              <div class="device-chips">
                <div 
                  v-for="device in selectedDevices" 
                  :key="device.id"
                  class="device-chip"
                >
                  <div class="chip-icon" :style="{ backgroundColor: getDeviceColor(device.type) }">
                    <i :class="getDeviceIcon(device.type)"></i>
                  </div>
                  <span>{{ device.name }}</span>
                </div>
              </div>
            </div>
            
            <div class="device-preview">
              <h4>设备状态预览</h4>
              <div class="preview-list">
                <div 
                  v-for="device in selectedDevices" 
                  :key="device.id"
                  class="preview-item"
                >
                  <div class="preview-info">
                    <div class="preview-icon" :style="{ backgroundColor: getDeviceColor(device.type) }">
                      <i :class="getDeviceIcon(device.type)"></i>
                    </div>
                    <div>
                      <h5>{{ device.name }}</h5>
                      <p>{{ device.room }} · {{ device.type }}</p>
                    </div>
                  </div>
                  <div class="preview-status">
                    <span v-if="!deviceStates[device.id].status" class="status-off">关闭</span>
                    <template v-else>
                      <span v-if="device.type === 'light'">
                        亮度 {{ deviceStates[device.id].brightness }}%
                      </span>
                      <span v-else-if="device.type === 'ac'">
                        {{ deviceStates[device.id].temperature }}°C
                      </span>
                      <span v-else>开启</span>
                    </template>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <button class="back-btn" @click="step = 2">
              <i class="fas fa-arrow-left"></i> 上一步
            </button>
            <button class="submit-btn" @click="createScene">
              <i class="fas fa-check"></i> 确认创建
            </button>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const store = useStore()
    const router = useRouter()
    
    // 步骤控制
    const step = ref(1)
    
    // 场景数据
    const scene = ref({
      name: '',
      description: '',
      icon: 'home'
    })
    
    // 设备选择相关
    const deviceSearch = ref('')
    const selectedRoom = ref('all')
    const deviceStates = ref({})
    
    // 获取设备列表
    const devices = computed(() => store.state.devices || [])
    const rooms = computed(() => store.state.rooms || [])
    
    // 场景图标选项
    const sceneIcons = ref([
      { id: 'home', class: 'fas fa-home', label: '回家' },
      { id: 'bed', class: 'fas fa-bed', label: '睡眠' },
      { id: 'sun', class: 'fas fa-sun', label: '起床' },
      { id: 'film', class: 'fas fa-film', label: '观影' },
      { id: 'utensils', class: 'fas fa-utensils', label: '用餐' },
      { id: 'door-open', class: 'fas fa-door-open', label: '离家' }
    ])
    
    // 初始化设备状态
    const initializeDeviceStates = () => {
      devices.value.forEach(device => {
        deviceStates.value[device.id] = {
          selected: false,
          status: device.status || false,
          ...(device.type === 'light' && { brightness: device.brightness || 50 }),
          ...(device.type === 'ac' && { temperature: device.temperature || 22 }),
          ...(device.type === 'curtain' && { openPercentage: device.openPercentage || 0 })
        }
      })
    }
    
    // 过滤设备
    const filteredDevices = computed(() => {
      let result = devices.value
      
      // 按房间过滤
      if (selectedRoom.value !== 'all') {
        result = result.filter(device => device.room === selectedRoom.value)
      }
      
      // 按搜索词过滤
      if (deviceSearch.value) {
        const searchTerm = deviceSearch.value.toLowerCase()
        result = result.filter(device => 
          device.name.toLowerCase().includes(searchTerm) || 
          device.type.toLowerCase().includes(searchTerm)
        )
      }
      
      return result
    })
    
    // 选中的设备
    const selectedDevices = computed(() => {
      return devices.value.filter(device => 
        deviceStates.value[device.id]?.selected
      )
    })
    
    const selectedDeviceCount = computed(() => selectedDevices.value.length)
    
    // 切换设备选择
    const toggleDeviceSelection = (deviceId) => {
      deviceStates.value[deviceId].selected = !deviceStates.value[deviceId].selected
    }
    
    // 检查设备是否被选中
    const isDeviceSelected = (deviceId) => {
      return deviceStates.value[deviceId]?.selected
    }
    
    // 获取设备图标
    const getDeviceIcon = (type) => {
      const iconMap = {
        light: 'fas fa-lightbulb',
        ac: 'fas fa-wind',
        monitor: 'fas fa-video',
        tv: 'fas fa-tv',
        curtain: 'fas fa-border-none',
        outlet: 'fas fa-plug'
      }
      return iconMap[type] || 'fas fa-microchip'
    }
    
    // 获取场景图标
    const getSceneIcon = (icon) => {
      return `fas fa-${icon}`
    }
    
    // 获取设备颜色
    const getDeviceColor = (type) => {
      const colorMap = {
        light: '#FF9800',
        ac: '#03A9F4',
        monitor: '#9C27B0',
        tv: '#E91E63',
        curtain: '#4CAF50',
        outlet: '#795548'
      }
      return colorMap[type] || '#607D8B'
    }
    
    // 返回处理
    const handleBack = () => {
      if (step.value > 1) {
        step.value -= 1
      } else {
        router.push('/')
      }
    }
    
    // 创建场景
    const createScene = () => {
      // 获取选中的设备及其状态
      const selectedDevicesWithState = selectedDevices.value.map(device => {
        const state = deviceStates.value[device.id]
        return {
          id: device.id,
          name: device.name,
          type: device.type,
          brand: device.brand,
          room: device.room,
          status: state.status,
          ...(device.type === 'light' && { brightness: state.brightness }),
          ...(device.type === 'ac' && { temperature: state.temperature }),
          ...(device.type === 'curtain' && { openPercentage: state.openPercentage })
        }
      })
      
      // 创建场景对象
      const newScene = {
        id: Date.now().toString(),
        name: scene.value.name,
        description: scene.value.description,
        icon: scene.value.icon,
        devices: selectedDevicesWithState
      }
      
      // 保存到Vuex
      store.dispatch('createScene', newScene)
      
      // 提示并返回首页
      alert(`场景"${newScene.name}"创建成功！`)
      router.push('/')
    }
    
    // 生命周期钩子
    onMounted(() => {
      initializeDeviceStates()
      store.dispatch('fetchDevices')
      store.dispatch('fetchRooms')
    })
    
    return {
      step,
      scene,
      deviceSearch,
      selectedRoom,
      deviceStates,
      devices,
      rooms,
      sceneIcons,
      filteredDevices,
      selectedDevices,
      selectedDeviceCount,
      toggleDeviceSelection,
      isDeviceSelected,
      handleBack,
      createScene,
      getDeviceIcon,
      getSceneIcon,
      getDeviceColor
    }
  }
}
</script>

<style lang="scss" scoped>
.create-scene {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: #f8fafc;
  min-height: 100vh;
}

.header {
  position: relative;
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e6ed;

  &__title {
    color: #2c3e50;
    margin: 20px 0;
    font-size: 28px;
    font-weight: 600;
  }

  &__steps {
    display: flex;
    justify-content: center;
    gap: 30px;
    margin-top: 20px;

    span {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: #e0e6ed;
      color: #90a4ae;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      position: relative;

      &.active {
        background: #2196f3;
        color: white;
      }

      &:not(:last-child):after {
        content: '';
        position: absolute;
        width: 30px;
        height: 2px;
        background: #e0e6ed;
        left: 100%;
        top: 50%;
        transform: translateY(-50%);
      }
    }
  }
}

.back-btn {
  position: absolute;
  left: 0;
  top: 0;
  display: flex;
  align-items: center;
  padding: 8px 15px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 20px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
  border: none;
  cursor: pointer;
  
  i {
    margin-right: 5px;
  }
  
  &:hover {
    background: #bbdefb;
  }
}

.form-container {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

.form-section {
  transition: all 0.3s ease;
}

.section-title {
  color: #2c3e50;
  margin-top: 0;
  margin-bottom: 25px;
  font-size: 22px;
  display: flex;
  align-items: center;
  gap: 10px;

  i {
    color: #2196f3;
  }
}

.form-group {
  margin-bottom: 25px;

  label {
    display: block;
    margin-bottom: 10px;
    font-weight: 500;
    color: #546e7a;
    display: flex;
    align-items: center;
    gap: 8px;

    i {
      color: #78909c;
      font-size: 14px;
    }
  }

  input, textarea {
    width: 100%;
    padding: 12px 15px;
    border: 2px solid #e0e6ed;
    border-radius: 10px;
    font-size: 16px;
    transition: all 0.3s;

    &:focus {
      border-color: #2196f3;
      box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
      outline: none;
    }
  }

  textarea {
    min-height: 100px;
    resize: vertical;
  }
}

.char-counter {
  text-align: right;
  font-size: 12px;
  color: #78909c;
  margin-top: 5px;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 15px;
}

.icon-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px 10px;
  border-radius: 10px;
  background: #f8f9fa;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }

  &.selected {
    background: #e3f2fd;
    border-color: #2196f3;
  }
}

.icon-wrapper {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  font-size: 24px;
  color: white;

  &.home { background: linear-gradient(135deg, #2196f3, #1976d2); }
  &.bed { background: linear-gradient(135deg, #9c27b0, #673ab7); }
  &.sun { background: linear-gradient(135deg, #FF9800, #FFC107); }
  &.film { background: linear-gradient(135deg, #f44336, #e91e63); }
  &.utensils { background: linear-gradient(135deg, #4CAF50, #8BC34A); }
  &.door-open { background: linear-gradient(135deg, #607d8b, #455a64); }
}

.search-filter {
  margin-bottom: 20px;
}

.search-box {
  position: relative;
  margin-bottom: 15px;

  i {
    position: absolute;
    left: 15px;
    top: 50%;
    transform: translateY(-50%);
    color: #90a4ae;
  }

  input {
    width: 100%;
    padding: 10px 15px 10px 40px;
    border: 2px solid #e0e6ed;
    border-radius: 20px;
    font-size: 14px;

    &:focus {
      border-color: #2196f3;
      outline: none;
    }
  }
}

.room-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-btn {
  background: #f0f4f8;
  color: #2c3e50;
  border: none;
  padding: 8px 15px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;

  &:hover {
    background: #e0e6ed;
  }

  &.active {
    background: #2196f3;
    color: white;
  }
}

.device-list {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 10px;
}

.device-item {
  border: 1px solid #e0e6ed;
  border-radius: 10px;
  margin-bottom: 15px;
  overflow: hidden;
  transition: all 0.3s;

  &.selected {
    border-color: #2196f3;
    box-shadow: 0 4px 12px rgba(33, 150, 243, 0.15);
  }
}

.device-info {
  display: flex;
  align-items: center;
  padding: 15px;
  cursor: pointer;
  background: #f8f9fa;
  transition: background 0.3s;

  .device-item.selected & {
    background: #e3f2fd;
  }

  &:hover {
    background: #f1f5f9;
  }
}

.device-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  margin-right: 15px;

  i {
    filter: drop-shadow(0 2px 2px rgba(0, 0, 0, 0.2));
  }
}

.device-details {
  flex-grow: 1;

  h3 {
    margin: 0 0 5px 0;
    color: #2c3e50;
    font-size: 16px;
  }

  p {
    margin: 0;
    color: #78909c;
    font-size: 13px;
  }
}

.device-check {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e0e6ed;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;

  .device-item.selected & {
    background: #2196f3;
  }
}

.device-controls {
  padding: 15px;
  background: #f8fafc;
  border-top: 1px solid #e0e6ed;
}

.control-group {
  display: flex;
  align-items: center;
  margin-bottom: 15px;

  &:last-child {
    margin-bottom: 0;
  }

  label {
    width: 80px;
    font-weight: 500;
    color: #546e7a;
  }

  input[type="range"] {
    flex-grow: 1;
    margin: 0 15px;
  }

  span {
    width: 50px;
    text-align: right;
    color: #37474f;
    font-weight: 500;
  }
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;

  input {
    opacity: 0;
    width: 0;
    height: 0;

    &:checked + label {
      background-color: #2196f3;
    }

    &:checked + label:before {
      transform: translateX(26px);
    }
  }

  label {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: .4s;
    border-radius: 24px;

    &:before {
      position: absolute;
      content: "";
      height: 18px;
      width: 18px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      transition: .4s;
      border-radius: 50%;
    }
  }
}

.no-devices {
  text-align: center;
  padding: 40px;
  color: #90a4ae;

  i {
    font-size: 48px;
    margin-bottom: 15px;
    opacity: 0.5;
  }

  p {
    margin: 0;
    font-size: 16px;
  }
}

.scene-summary {
  margin-bottom: 30px;
}

.scene-header {
  display: flex;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e6ed;
}

.scene-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  color: white;
  margin-right: 20px;

  &.home { background: linear-gradient(135deg, #2196f3, #1976d2); }
  &.bed { background: linear-gradient(135deg, #9c27b0, #673ab7); }
  &.sun { background: linear-gradient(135deg, #FF9800, #FFC107); }
  &.film { background: linear-gradient(135deg, #f44336, #e91e63); }
  &.utensils { background: linear-gradient(135deg, #4CAF50, #8BC34A); }
  &.door-open { background: linear-gradient(135deg, #607d8b, #455a64); }
}

.scene-details {
  flex-grow: 1;

  h3 {
    margin: 0 0 5px 0;
    color: #2c3e50;
    font-size: 24px;
  }

  p {
    margin: 0;
    color: #78909c;
    font-size: 14px;
  }
}

.selected-devices {
  margin-bottom: 25px;

  h4 {
    margin: 0 0 15px 0;
    color: #546e7a;
    font-size: 16px;
  }
}

.device-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.device-chip {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  background: #f0f4f8;
  border-radius: 20px;
  font-size: 14px;
}

.chip-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  margin-right: 8px;
}

.device-preview {
  h4 {
    margin: 0 0 15px 0;
    color: #546e7a;
    font-size: 16px;
  }
}

.preview-list {
  border: 1px solid #e0e6ed;
  border-radius: 10px;
  overflow: hidden;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #e0e6ed;
  background: #f8f9fa;

  &:last-child {
    border-bottom: none;
  }
}

.preview-info {
  display: flex;
  align-items: center;

  h5 {
    margin: 0 0 5px 0;
    color: #2c3e50;
    font-size: 16px;
  }

  p {
    margin: 0;
    color: #78909c;
    font-size: 13px;
  }
}

.preview-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  margin-right: 15px;
}

.preview-status {
  font-weight: 500;
  color: #2c3e50;

  .status-off {
    color: #f44336;
  }
}

.form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
}

.next-btn, .submit-btn {
  padding: 12px 25px;
  background: linear-gradient(to right, #2196f3, #1976d2);
  color: white;
  border: none;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(33, 150, 243, 0.3);
  }

  &:disabled {
    background: #e0e6ed;
    color: #90a4ae;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
}

.submit-btn {
  background: linear-gradient(to right, #4CAF50, #2E7D32);
}

.back-btn {
  padding: 12px 25px;
  background: #f0f4f8;
  color: #546e7a;
  border: none;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover {
    background: #e0e6ed;
  }
}

/* 过渡动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>