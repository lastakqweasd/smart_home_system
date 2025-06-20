<template>
  <div class="home-page">
    <header class="header">
      <h1 class="header__title">智能家居控制中心</h1>
      <router-link to="/add-device" class="add-device-btn">添加设备</router-link>
      <div class="auth-info">
        用户
        <template v-if="$store.getters.isAuthenticated">
          <span class="user-name">欢迎，{{ $store.state.user.username}}</span>
          <button @click="handleLogout" class="logout-btn">注销</button>
        </template>
        <router-link v-else to="/login" class="login-link">登录</router-link>
      </div>
    </header>

    <div class="filter-section">
      <button
        class="filter-btn"
        :class="{ active: selectedRoom === 'all' }"
        @click="setSelectedRoom('all')"
      >
        全部
      </button>
      <button
        v-for="room in rooms"
        :key="room.id"
        class="filter-btn"
        :class="{ active: selectedRoom === room.id }"
        @click="setSelectedRoom(room.id)"
      >
        {{ room.name }}
      </button>
    </div>

    <!-- 在场所选择栏下面添加设备类型选择栏 -->
    <div class="filter-section">
      <button
        class="filter-btn"
        :class="{ active: selectedDeviceType === 'all' }"
        @click="setSelectedDeviceType('all')"
      >
        全部设备
      </button>
      
      <button
        v-for="type in deviceTypes"
        :key="type.value"
        class="filter-btn"
        :class="{ active: selectedDeviceType === type.value }"
        @click="setSelectedDeviceType(type.value)"
      >
        <i :class="type.icon" style="margin-right: 5px;"></i>
        {{ type.label }}
      </button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="devices-section">
      <h2>设备列表</h2>
      <div class="scrollable-container">
        <div class="scrollable-content">
          <device-card
            v-for="device in filteredDevices"
            :key="device.id"
            :device="device"
            :rooms="rooms"
            class="scrollable-item"
          />
        </div>
      </div>
    </div>

    <room-management 
      :rooms="rooms"
      :devices="devices"
      @create-room="handleCreateRoom"
      @update-room="handleUpdateRoom"
      @delete-room="handleDeleteRoom"
    />

    <div class="scenes-section">
      <div class="scenes-header">
        <h2 class="scenes-section__title">场景模式</h2>
      </div>
      <router-link to="/create-scene" class="create-scene-link">创建场景模式</router-link>
      
      <div v-if="scenes.length === 0" class="no-scenes">
        <i class="fas fa-scroll"></i>
        <p>暂无场景模式</p>
      </div>

      <div v-else class="scrollable-container">
        <div class="scrollable-content">
          <div
            v-for="scene in scenes"
            :key="scene.id"
            class="scene-card scrollable-item"
            @click="activateScene(scene.id)"
          >
            <div class="scene-icon" :class="scene.icon">
              <i :class="getSceneIcon(scene.icon)"></i>
            </div>
            <div class="scene-info">
              <h3 class="scene-card__title">{{ scene.name }}</h3>
              <p class="scene-card__desc">{{ scene.description }}</p>
              <div class="scene-device-count">
                <!-- <i class="fas fa-microchip"></i> {{scene.devices.length}} 个设备 -->
                <i class="fas fa-microchip"></i> {{scene.device_configs.length }} 个设备
              </div>
            </div>
            <button 
              class="delete-scene-btn" 
              title="删除"
              @click.stop="confirmDeleteScene(scene)"
            >
              <i class="fas fa-trash-alt"></i>
            </button>
            <button 
              class="scene-detail-btn"
              title="详情"
              @click.stop="showSceneDetail(scene)"
            >
              <i class="fas fa-info-circle"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="sceneToDelete" class="delete-confirm-modal">
      <div class="modal-content">
        <h3>确认删除场景</h3>
        <p>确定要删除场景 <strong>"{{ sceneToDelete.name }}"</strong> 吗？此操作无法撤销。</p>
        <div class="modal-actions">
          <button class="cancel-btn" @click.stop="sceneToDelete = null">取消</button>
          <button class="cancel-btn" @click.stop="deleteScene(sceneToDelete.id)">删除</button>
        </div>
      </div>
    </div>

    <div v-if="sceneToShowDetail" class="scene-detail-modal">
      <div class="modal-content">
        <div class="scene-header">
          <!-- <div class="scene-icon" :class="sceneToShowDetail.icon">
            <i :class="getSceneIcon(sceneToShowDetail.icon)"></i>
          </div> -->
          <div class="scene-title-info">
            <h3>{{ sceneToShowDetail.name }}</h3>
            <p>{{ sceneToShowDetail.description }}</p>
          </div>
        </div>
        
        <div class="device-list-section">
          <h4>设备设置 <span class="device-count">({{ sceneToShowDetail.device_configs.length }}个设备)</span></h4>
          <div class="device-list">
            <div v-for="device in scene_device_info" :key="device.id" class="device-item">
              <div class="device-info" @click="scene_toggleDeviceSelection(device.id)">
                <div class="device-details">
                  <div class="device-icon">
                    <i :class="getDeviceIcon(device.type)"></i>
                  </div>
                  <h3>{{ device.name }}</h3>
                  <!-- <p>{{ device.roomName }} · {{ device.type }}</p> -->
                  <p>房间:{{device.roomName}}   类型:{{ device.type }}</p>
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
        
        <div class="modal-actions">
          <button class="activate-btn" @click="activateScene(sceneToShowDetail.id); sceneToShowDetail = null">执行此场景</button>
          <button class="save-changes-btn" @click.stop="saveSceneChanges(); sceneToShowDetail = null">保存修改</button>
          <button class="close-modal-btn" @click.stop="sceneToShowDetail = null">关闭</button>
        </div>
      
      </div>
    </div>
  </div>

</template>

<script>
import { computed, onMounted, ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import DeviceCard from '@/components/devices/DeviceCard.vue'
import RoomManagement from '@/views/RoomManagement.vue'

export default {
  name: 'HomePage',
  components: {
    DeviceCard,
    RoomManagement
  },
  setup() {
    const store = useStore()
    const router = useRouter()

    // 获取状态
    const devices = computed(() => store.state.devices || [])
    const rooms = computed(() => store.state.rooms || [])
    const scenes = computed(() => store.state.scenes || [])
    const selectedRoom = computed(() => store.state.selectedRoom || 'all')
    const loading = computed(() => store.state.loading || false)
    const error = computed(() => store.state.error || null)

    const sceneToDelete = ref(null)
    const sceneToShowDetail = ref(null)
    //保存在这里更改的设备信息
    const deviceStates = ref({})
    //由于场景中只有设备id，没有设备名称，
    // 因此配套一个scene_device_info来记录对应场景的设备信息
    const scene_device_info = computed(() => {
      if (!sceneToShowDetail.value?.device_configs || !devices.value) {
        return []; // 返回空数组避免 undefined 问题
      }

      return sceneToShowDetail.value.device_configs
        .map((deviceConfig) => {
          // 在 devices 中查找匹配的设备
          const matchedDevice = devices.value.find(
            (d) => d.id === deviceConfig.device
          );
          if (!matchedDevice) {
            console.warn(`Device not found: ${deviceConfig.device}`);
            return null; // 过滤掉未匹配的设备
          }
          const room = rooms.value.find(r => r.id === matchedDevice.room);
          // 合并设备基础信息和场景配置
          return {
            ...matchedDevice, // 设备原始信息（id, name, type等）
            ...deviceConfig, // 场景中的配置（status, config等）
            roomName: room?.name || '未知房间'
          };
        })
        .filter(Boolean); // 移除 null 项（未匹配的设备）
    });

    // 设备类型定义
    const deviceTypes = ref([
      { value: 'light', label: '智能灯', icon: 'fas fa-lightbulb' },
      { value: 'ac', label: '空调', icon: 'fas fa-snowflake' },
      { value: 'outlet', label: '智能插座', icon: 'fas fa-plug' },
      { value: 'curtain', label: '智能窗帘', icon: 'fas fa-window-maximize' },
      { value: 'tv', label: '智能电视', icon: 'fas fa-tv' },
      { value: 'monitor', label: '监控摄像头', icon: 'fas fa-video' }
    ])

    // 选中的设备类型
    const selectedDeviceType = ref('all')

    // 设置选中的设备类型
    const setSelectedDeviceType = (type) => {
      selectedDeviceType.value = type
    }

    // 过滤设备列表（同时考虑场所和设备类型）
    const filteredDevices = computed(() => {
      let filtered = devices.value
      // 按场所过滤
      if (selectedRoom.value !== 'all') {
        filtered = filtered.filter(device => device.roomId === selectedRoom.value)
      }
      
      // 按设备类型过滤
      if (selectedDeviceType.value !== 'all') {
        filtered = filtered.filter(device => device.type === selectedDeviceType.value)
      }
      console.log("房间")
      console.log(rooms)
      return filtered
    })

    // 方法
    const setSelectedRoom = (room) => {
      store.dispatch('setSelectedRoom', room)
    }

    const activateScene = (sceneId) => {
      store.dispatch('activateScene', sceneId)
    }

    const confirmDeleteScene = (scene) => {
      sceneToDelete.value = scene
    }

    const deleteScene = (sceneId) => {
      store.dispatch('deleteScene', sceneId)
      sceneToDelete.value = null
    }

    const handleLogout = () => {
      store.dispatch('logout')
      router.push('/login')
    }

  // 房间管理相关状态
    const handleCreateRoom = (roomName) => {
      store.dispatch('createRoom', { name: roomName })
    }

    const handleUpdateRoom = ({ roomId, newName }) => {
      store.dispatch('updateRoom', {
        roomId,
        newName
      })
    }

    const handleDeleteRoom = (roomId) => {
      store.dispatch('deleteRoom', roomId)
    }

    const getSceneIcon = (icon) => {
      const iconMap = {
        home: 'fas fa-home',
        bed: 'fas fa-bed',
        sun: 'fas fa-sun',
        film: 'fas fa-film',
        utensils: 'fas fa-utensils',
        'door-open': 'fas fa-door-open'
      }
      return iconMap[icon] || 'fas fa-scroll'
    }

    // 获取设备图标
    const getDeviceIcon = (type) => {
      const iconMap = {
        light: 'fas fa-lightbulb',
        ac: 'fas fa-snowflake',
        outlet: 'fas fa-plug',
        curtain: 'fas fa-window-maximize',
        tv: 'fas fa-tv',
        monitor: 'fas fa-video',
        switch: 'fas fa-toggle-on',
        sensor: 'fas fa-wifi'
      };
      return iconMap[type] || 'fas fa-microchip';
    };

    const showSceneDetail = (scene) => {
      sceneToShowDetail.value = scene
      // 初始化设备状态
      scene.device_configs.forEach(device => {
        //根据设备id找到对应设备信息
        const detail_device = devices.value.find(d => d.id === device.device)
        deviceStates.value[device.device] = {
          selected: false,
          status: device.status || false,
          ...(detail_device.type === 'light' && { brightness: device.config.brightness || 50 }),
          ...(detail_device.type === 'ac' && { temperature: device.config.temperature || 22 }),
          ...(detail_device.type === 'curtain' && { openPercentage: device.config.openPercentage || 0 })
        }
      })
      console.log("查看要显示的场景")
      console.log(sceneToShowDetail)
      console.log("查看设备")
      console.log(scene_device_info.value)
      console.log("查看场景设备状态")
      console.log(deviceStates.value)
      console.log("查看全部场景状态")
      console.log(scenes.value)
    }

    const scene_toggleDeviceSelection = (deviceId) => {
      deviceStates.value[deviceId].selected = !deviceStates.value[deviceId].selected
    }

    const isDeviceSelected = (deviceId) => {
      return deviceStates.value[deviceId]?.selected || false
    }

    const saveSceneChanges = async () => {
      if (!sceneToShowDetail.value) return;

      try {
        const sceneId = sceneToShowDetail.value.id;
        const devicesToUpdate = [];
        
        for (const deviceId in deviceStates.value) {
          const deviceState = deviceStates.value[deviceId];
          const cur_device = devices.value.find(d => d.id === deviceId);
          
          if (cur_device) {
            devicesToUpdate.push({
              id: deviceId,
              status: deviceState.status,
              ...(deviceState.brightness !== undefined && { brightness: deviceState.brightness }),
              ...(deviceState.temperature !== undefined && { temperature: deviceState.temperature }),
              ...(deviceState.openPercentage !== undefined && { openPercentage: deviceState.openPercentage })
            });
          }
        }
        
        await store.dispatch('updateSceneDevices', {
          sceneId,
          devices: devicesToUpdate
        });
        
        alert('场景修改已保存！');
      } catch (error) {
        console.error('保存场景失败:', error);
        alert('保存场景失败，请重试');
      }
    };

    // 生命周期钩子
    onMounted(() => {
      store.dispatch('fetchDevices')
      store.dispatch('fetchRooms')
      store.dispatch('fetchScenes')
    })

    return {
      devices,
      rooms,
      scenes,
      selectedRoom,
      loading,
      error,
      filteredDevices,
      sceneToDelete,
      sceneToShowDetail,
      deviceStates,
      setSelectedRoom,
      activateScene,
      confirmDeleteScene,
      deleteScene,
      handleLogout,
      getSceneIcon,
      handleCreateRoom,
      handleUpdateRoom,
      handleDeleteRoom,
      getDeviceIcon,
      showSceneDetail,
      scene_toggleDeviceSelection,
      isDeviceSelected,
      saveSceneChanges,
      deviceTypes,
      selectedDeviceType,
      setSelectedDeviceType,
      scene_device_info
    }
  }
}
</script>

<style lang="scss" scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    position: relative;

    &__title {
      color: #333;
      margin: 0;
    }
  }

  .auth-info {
    display: flex;
    align-items: center;
    gap: 15px;

    .user-name {
      font-weight: 500;
      color: #393939;
    }

    .logout-btn {
      padding: 6px 12px;
      background: #ff4444;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      transition: background 0.2s;

      &:hover {
        background: #cc0000;
      }
    }

    .login-link {
      color: #42b983;
      text-decoration: none;
      font-weight: 600;
      padding: 8px 16px;
      border: 2px solid #42b983;
      border-radius: 4px;

      &:hover {
        background: #f0faf5;
      }
    }
  }

  /* 房间管理样式 */
.room-management {
  margin-bottom: 25px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.add-room-btn {
  padding: 8px 15px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 15px;
  
  i {
    margin-right: 5px;
  }
  
  &:hover {
    background: #3d8b40;
  }
}

.room-list {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.room-item {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.room-name {
  min-width: 120px;
  font-weight: 500;
  cursor: pointer;
  padding: 5px;
  
  &:hover {
    background: #f0f0f0;
  }
}

.room-name-input {
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 120px;
}

.room-actions {
  margin-left: 10px;
  display: flex;
  gap: 5px;
}

.edit-btn, .delete-btn {
  padding: 5px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  
  i {
    font-size: 14px;
  }
}

.edit-btn {
  background: #ffc107;
  color: #333;
  
  &:hover {
    background: #e0a800;
  }
}

.delete-btn {
  background: #dc3545;
  color: white;
  
  &:hover {
    background: #c82333;
  }
}

  .filter-section {
    margin-bottom: 20px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }

  .filter-btn {
    background: #f0f0f0;
    color: #333;
    border: none;
    padding: 8px 15px;
    border-radius: 20px;
    cursor: pointer;

    &:hover {
      background: #e0e0e0;
    }

    &.active {
      background: #2196f3;
      color: white;

      &:hover {
        background: #1976d2;
      }
    }
  }

  .scrollable-container {
    width: 100%;
    overflow-x: auto;
    padding: 20px 0;
    margin: 10px 0;
    -webkit-overflow-scrolling: touch;

    &::-webkit-scrollbar {
      height: 8px;
      background-color: #f5f5f5;
    }

    &::-webkit-scrollbar-thumb {
      background-color: #2196f3;
      border-radius: 4px;
    }
  }

  .scrollable-content {
    display: inline-flex;
    gap: 20px;
    padding: 0 20px;
  }

  .scrollable-item {
    flex: 0 0 auto;
    width: 280px;
  }

  .device-card {
    margin: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.2s;
    
    &:hover {
      transform: translateY(-3px);
    }
  }

  .scene-card {
    position: relative;
    display: flex;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    cursor: pointer;
    transition: all 0.3s;
    border: 1px solid #e0e6ed;
    width: 300px;
    
    &:hover {
      transform: translateY(-3px);
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
      border-color: #2196f3;
    }
  }

  .scene-icon {
    width: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #2196f3, #1976d2);
    color: white;
    font-size: 28px;
    
    &.home { background: linear-gradient(135deg, #2196f3, #1976d2); }
    &.bed { background: linear-gradient(135deg, #9c27b0, #673ab7); }
    &.sun { background: linear-gradient(135deg, #ff9800, #ff5722); }
    &.film { background: linear-gradient(135deg, #f44336, #e91e63); }
    &.utensils { background: linear-gradient(135deg, #4caf50, #8bc34a); }
    &.door-open { background: linear-gradient(135deg, #607d8b, #455a64); }
  }

  .scene-info {
    flex: 1;
    padding: 20px;
  }

  .scene-card__title {
    margin: 0 0 8px 0;
    font-size: 18px;
    color: #2c3e50;
  }

  .scene-card__desc {
    margin: 0 0 12px 0;
    color: #666;
    font-size: 14px;
    line-height: 1.4;
  }

  .scene-device-count {
    display: flex;
    align-items: center;
    color: #78909c;
    font-size: 13px;
    
    i {
      margin-right: 5px;
      font-size: 12px;
    }
  }

  .no-scenes {
    text-align: center;
    padding: 40px 20px;
    background: #f8f9fa;
    border-radius: 12px;
    border: 1px dashed #e0e6ed;
    
    i {
      font-size: 48px;
      color: #bbdefb;
      margin-bottom: 15px;
    }
    
    p {
      margin: 0 0 20px 0;
      color: #78909c;
      font-size: 16px;
    }
  }

  .create-scene-link {
    display: inline-block;
    padding: 10px 20px;
    background: linear-gradient(to right, #2196f3, #1976d2);
    color: white;
    text-decoration: none;
    border-radius: 30px;
    font-weight: 500;
    transition: all 0.3s;
    margin-bottom: 20px;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(33, 150, 243, 0.3);
    }
  }

  .add-device-btn {
    background: #2196f3;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 20px;
    cursor: pointer;
    text-decoration: none;
    font-size: 14px;

    &:hover {
      background: #1976d2;
    }
  }

  .delete-scene-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 30px;
    height: 30px;
    color: white;
    border: none;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
    z-index: 10;
    opacity: 1;
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);

    &:hover {
      background: #d32f2f;
      transform: scale(1.1);
      box-shadow: 0 3px 6px rgba(0,0,0,0.3);
    }
  }

  .scene-detail-btn {
    position: absolute;
    top: 10px;
    right: 50px;
    width: 30px;
    height: 30px;
    background: rgba(33, 150, 243, 0.9);
    color: white;
    border: none;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    z-index: 2;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    
    i {
      font-size: 14px;
      transition: transform 0.2s;
    }
    
    &:hover {
      background: #1976d2;
      transform: scale(1.1);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
      
      i {
        transform: scale(1.2);
      }
    }
    
    &:active {
      transform: scale(0.95);
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    &:focus {
      outline: none;
      box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.3);
    }
  }

  .delete-confirm-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .scene-detail-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    backdrop-filter: blur(3px);
  }

  .modal-content {
    background: white;
    border-radius: 12px;
    padding: 25px;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    
    h3 {
      margin-top: 0;
      color: #333;
      font-size: 20px;
    }
    
    p {
      margin: 15px 0 25px;
      color: #666;
      line-height: 1.6;
      
      strong {
        color: #e53935;
      }
    }
  }

  .scene-header {
    display: flex;
    align-items: center;
    margin-bottom: 25px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
    
    .scene-icon {
      width: 70px;
      height: 70px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 32px;
      color: white;
      margin-right: 20px;
      flex-shrink: 0;
    }
    
    .scene-title-info {
      h3 {
        margin: 0 0 8px 0;
        font-size: 24px;
        color: #2c3e50;
      }
      
      p {
        margin: 0;
        color: #666;
        font-size: 16px;
        line-height: 1.5;
      }
    }
  }

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 15px;
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #eee;
    
    .activate-btn {
      padding: 12px 25px;
      background: linear-gradient(to right, #4caf50, #2e7d32);
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 500;
      transition: all 0.3s;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
      }
    }
    
    .save-changes-btn {
      padding: 12px 25px;
      background: linear-gradient(to right, #2196f3, #1976d2);
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 500;
      transition: all 0.3s;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(33, 150, 243, 0.3);
      }
    }
    
    .close-modal-btn {
      padding: 12px 25px;
      background: #f5f5f5;
      color: #666;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 500;
      transition: all 0.3s;
      
      &:hover {
        background: #e0e0e0;
      }
    }
  }

  .device-list-section {
    margin-bottom: 25px;
    
    h4 {
      margin: 0 0 15px 0;
      font-size: 18px;
      color: #333;
      display: flex;
      align-items: center;
      
      .device-count {
        margin-left: 8px;
        font-size: 14px;
        color: #777;
        font-weight: normal;
      }
    }
  }

  .device-list {
    max-height: 300px;
    overflow-y: auto;
    padding-right: 10px;
  }

  .device-info {
    display: flex;
    align-items: center;
    padding: 15px;
    cursor: pointer;
    background: #f8f9fa;
    transition: background 0.3s;
    
    &:hover {
      background: #f1f5f9;
    }
  }

  .device-details {
    flex-grow: 1;
    
    h3 {
      font-weight: 500;
      color: #333;
      margin-bottom: 3px;
    }
    
    p {
      font-size: 13px;
      color: #78909c;
      margin: 0;
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

  .loading,
  .error {
    padding: 20px;
    text-align: center;

    &.error {
      color: #f44336;
    }
  }
}

//取消
.cancel-btn {
  /* 基础样式 */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-family: 'Segoe UI', system-ui, sans-serif;
  font-weight: 500;
  font-size: 0.875rem;
  line-height: 1.25;
  cursor: pointer;
  transition: all 0.15s ease-out;
  user-select: none;
  
  /* 取消按钮特有样式 */
  background-color: transparent;
  color: #6b7280; /* 中性灰色 */
  border: 1px solid #e5e7eb; /* 浅灰色边框 */
  
  /* 间距优化 */
  gap: 0.375rem;
  
  /* 响应式调整 */
  @media (min-width: 640px) {
    padding: 0.625rem 1.5rem;
  }
}


</style>