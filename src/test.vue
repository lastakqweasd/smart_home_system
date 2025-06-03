<template>
  <div class="create-scene">
    <div class="header">
      <router-link to="/" class="back-btn">
        <i class="fas fa-arrow-left"></i> 返回首页
      </router-link>
      <h1>创建场景模式</h1>
    </div>

    <div class="scene-form">
      <div class="form-group">
        <label for="scene-name">场景名称</label>
        <input 
          type="text" 
          id="scene-name" 
          v-model="scene.name" 
          placeholder="例如：回家模式、睡眠模式" 
          maxlength="20"
        >
        <div class="char-counter">{{ scene.name.length }}/20</div>
      </div>

      <div class="form-group">
        <label for="scene-description">场景描述</label>
        <textarea 
          id="scene-description" 
          v-model="scene.description" 
          placeholder="描述此场景的功能和效果"
          maxlength="100"
        ></textarea>
        <div class="char-counter">{{ scene.description.length }}/100</div>
      </div>

      <div class="form-group">
        <label>场景图标</label>
        <div class="icon-selector">
          <div 
            v-for="icon in sceneIcons" 
            :key="icon.id"
            class="icon-option"
            :class="{ selected: scene.icon === icon.id }"
            @click="scene.icon = icon.id"
          >
            <i :class="icon.class"></i>
            <span>{{ icon.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="devices-section">
      <div class="section-header">
        <h2>选择设备</h2>
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            v-model="deviceSearch" 
            placeholder="搜索设备..."
          >
        </div>
      </div>

      <div class="device-filters">
        <button 
          v-for="room in rooms" 
          :key="room.id"
          class="filter-btn"
          :class="{ active: selectedRoom === room.name }"
          @click="setSelectedRoom(room.name)"
        >
          {{ room.name }}
        </button>
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
          </div>
          
          <div v-if="isDeviceSelected(device.id)" class="device-controls">
            <div class="control-group">
              <label>状态</label>
              <div class="toggle-switch">
                <input 
                  type="checkbox" 
                  :id="'power-' + device.id" 
                  v-model="deviceStates[device.id].status"
                >
                <label :for="'power-' + device.id"></label>
              </div>
            </div>
            
            <!-- 灯光控制 -->
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
            
            <!-- 空调控制 -->
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
            
            <!-- 窗帘控制 -->
            <div v-if="device.type === 'curtain'" class="control-group">
              <label>开合度</label>
              <input 
                type="range" 
                min="0" 
                max="100" 
                v-model="deviceStates[device.id].openPercentage"
                :disabled="!deviceStates[device.id].status"
              >
              <span>{{ deviceStates[device.id].openPercentage }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="actions">
      <button class="btn cancel" @click="cancelCreation">取消</button>
      <button class="btn create" @click="createScene">创建场景</button>
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
    
    // 场景数据 - 匹配db.json结构
    const scene = ref({
      name: '',
      description: '',
      icon: 'home',
      devices: [] // 设备数组将包含设备状态对象
    })
    
    // 设备搜索
    const deviceSearch = ref('')
    const selectedRoom = ref('all')
    
    // 设备状态
    const deviceStates = ref({})
    
    // 获取设备列表
    const devices = computed(() => store.state.devices)
    const rooms = computed(() => store.state.rooms)
    
    // 场景图标选项
    const sceneIcons = ref([
      { id: 'home', class: 'fas fa-home', label: '回家' },
      { id: 'bed', class: 'fas fa-bed', label: '睡眠' },
      { id: 'sun', class: 'fas fa-sun', label: '起床' },
      { id: 'film', class: 'fas fa-film', label: '观影' },
      { id: 'utensils', class: 'fas fa-utensils', label: '用餐' },
      { id: 'door-open', class: 'fas fa-door-open', label: '离家' }
    ])
    
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
    
    // 切换设备选择
    const toggleDeviceSelection = (deviceId) => {
      deviceStates.value[deviceId].selected = !deviceStates.value[deviceId].selected
    }
    
    // 检查设备是否被选中
    const isDeviceSelected = (deviceId) => {
      return deviceStates.value[deviceId]?.selected
    }
    
    // 设置选择的房间
    const setSelectedRoom = (room) => {
      selectedRoom.value = room
    }
    
    // 取消创建
    const cancelCreation = () => {
      router.push('/')
    }
    
    // 创建场景 - 匹配db.json结构
    const createScene = () => {
      if (!scene.value.name.trim()) {
        alert('请输入场景名称')
        return
      }
      
      // 获取选中的设备及其状态 - 匹配db.json结构
      const selectedDevices = []
      Object.keys(deviceStates.value).forEach(deviceId => {
        if (deviceStates.value[deviceId].selected) {
          const device = devices.value.find(d => d.id === deviceId)
          
          // 创建设备状态对象 - 匹配db.json结构
          const deviceStatus = {
            status: deviceStates.value[deviceId].status
          }
          
          // 根据设备类型添加额外属性
          if (device.type === 'light') {
            deviceStatus.brightness = deviceStates.value[deviceId].brightness
          } else if (device.type === 'ac') {
            deviceStatus.temperature = deviceStates.value[deviceId].temperature
          } else if (device.type === 'curtain') {
            deviceStatus.openPercentage = deviceStates.value[deviceId].openPercentage
          }
          
          // 添加到场景设备列表
          selectedDevices.push(deviceStatus)
        }
      })
      
      if (selectedDevices.length === 0) {
        alert('请至少选择一个设备')
        return
      }
      
      // 创建场景对象 - 匹配db.json结构
      const newScene = {
        id: Date.now().toString(),
        name: scene.value.name,
        description: scene.value.description,
        icon: scene.value.icon,
        devices: selectedDevices
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
      scene,
      deviceSearch,
      selectedRoom,
      deviceStates,
      devices,
      rooms,
      sceneIcons,
      filteredDevices,
      toggleDeviceSelection,
      isDeviceSelected,
      setSelectedRoom,
      cancelCreation,
      createScene,
      getDeviceIcon,
      getDeviceColor
    }
  }
}
</script>

<style lang="scss" scoped>
/* 样式保持不变 */
.create-scene {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e0e6ed;
  
  h1 {
    flex-grow: 1;
    text-align: center;
    color: #2c3e50;
    margin: 0;
  }
}

.back-btn {
  display: flex;
  align-items: center;
  padding: 8px 15px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 20px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
  
  i {
    margin-right: 5px;
  }
  
  &:hover {
    background: #bbdefb;
  }
}

.scene-form {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 25px;
  
  label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #2c3e50;
  }
  
  input, textarea {
    width: 100%;
    padding: 12px 15px;
    border: 2px solid #e0e6ed;
    border-radius: 8px;
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

.icon-selector {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 15px;
  margin-top: 10px;
}

.icon-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px 10px;
  border-radius: 10px;
  background: #f8f9fa;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
  
  i {
    font-size: 24px;
    color: #546e7a;
    margin-bottom: 8px;
  }
  
  span {
    font-size: 13px;
    color: #546e7a;
  }
  
  &:hover {
    background: #e3f2fd;
    border-color: #bbdefb;
  }
  
  &.selected {
    background: #e3f2fd;
    border-color: #2196f3;
    
    i, span {
      color: #1976d2;
    }
  }
}

.devices-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  h2 {
    margin: 0;
    color: #2c3e50;
  }
}

.search-box {
  position: relative;
  width: 300px;
  
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

.device-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
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

.actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px 0;
}

.btn {
  padding: 12px 30px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  
  &.cancel {
    background: #f0f4f8;
    color: #546e7a;
    
    &:hover {
      background: #e0e6ed;
    }
  }
  
  &.create {
    background: linear-gradient(to right, #2196f3, #1976d2);
    color: white;
    box-shadow: 0 4px 10px rgba(33, 150, 243, 0.3);
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 15px rgba(33, 150, 243, 0.4);
    }
  }
}
</style>