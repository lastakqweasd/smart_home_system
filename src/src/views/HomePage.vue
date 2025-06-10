<template>
  <div class="home-page">
    <header class="header">
      <h1 class="header__title">智能家居控制中心</h1>

      <!-- 新加 -->
      <router-link to="/add-device" class="add-device-btn">添加设备</router-link>

     <div class="auth-info">
        用户
        <template v-if="$store.getters.isAuthenticated">
          <span class="user-name">欢迎，{{ $store.getters.currentUser.name }}</span>
          <button @click="handleLogout" class="logout-btn">注销</button>
        </template>
        <router-link v-else to="/login" class="login-link">登录</router-link>
      </div>
    </header>
    <!-- 标题 -->

    <div class="filter-section">
      <button
        class="filter-btn"
        :class="{ active: selectedRoom === 'all' }"
        @click="setSelectedRoom('all')"
      >
      <!-- active动态绑定用来控制按钮颜色 -->
        全部
      </button>

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
    <!-- 房间选择栏 -->

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="devices-grid">
      <device-card
        v-for="device in filteredDevices"
        :key="device.id"
        :device="device"
      />
    </div>
    <!-- 具体设备网格 -->

    <!-- 场景创建部分 -->
    <div class="scenes-section">
      <div class="scenes-header">
        <h2 class="scenes-section__title">场景模式</h2>
        <div class="scene-count">({{ scenes.length }}个场景)</div>
      </div>
      <!-- 创建场景模式 -->
      <router-link to="/create-scene" class="create-scene-link">创建场景模式</router-link>
      <!-- 如果没有场景模式 -->
      <div v-if="scenes.length === 0" class="no-scenes">
        <i class="fas fa-scroll"></i>
        <p>暂无场景模式</p>
      </div>
      <!-- 场景模式列表 -->

      <div v-else class="scene-cards">
        <div
          v-for="scene in scenes"
          :key="scene.id"
          class="scene-card"
          @click="activateScene(scene.id)"
        >
        <!-- 场景内容 -->
        <div class="scene-icon" :class="scene.icon">
          <i :class="getSceneIcon(scene.icon)"></i>
        </div>
        <div class="scene-info">
          <h3 class="scene-card__title">{{ scene.name }}</h3>
          <p class="scene-card__desc">{{ scene.description }}</p>
          <div class="scene-device-count">
            <i class="fas fa-microchip"></i> {{scene.devices.length}} 个设备
          </div>
        </div>
        <!-- 删除按钮 -->
          <button 
            class="delete-scene-btn" 
            title="删除"
            @click.stop="confirmDeleteScene(scene)"
          >
            <i class="fas fa-trash-alt"></i>
          </button>
        <!-- 详情查看按钮 -->
          <button 
            class="scene-detail-btn"
            title="详情"
            @click.stop="ShowSceneDetail(scene)"
          >
            <i class="fas fa-info-circle"></i>
          </button>

        </div>
      </div>

      <div v-if="sceneToDelete" class="delete-confirm-modal">
        <div class="modal-content">
          <h3>确认删除场景</h3>
          <p>确定要删除场景 <strong>"{{ sceneToDelete.name }}"</strong> 吗？此操作无法撤销。</p>
          <div class="modal-actions">
            <button class="cancel-btn" @click.stop="sceneToDelete = null">取消</button>
            <button class="confirm-delete-btn" @click.stop="deleteScene(sceneToDelete.id)">删除</button>
          </div>
        </div>
      </div>
    </div>
    <!-- 场景模式部分 -->
  </div>

  <!-- 场景详情弹窗 -->
  <div v-if="sceneToShowDetail" class="scene-detail-modal">
    <div class="modal-content">
      
      <div class="scene-header">
        <div class="scene-icon" :class="sceneToShowDetail.icon">
          <i :class="getSceneIcon(sceneToShowDetail.icon)"></i>
        </div>
        <div class="scene-title-info">
          <h3>{{ sceneToShowDetail.name }}</h3>
          <p>{{ sceneToShowDetail.description }}</p>
        </div>
      </div>
      
      <div class="device-list-section">
        <h4>设备设置 <span class="device-count">({{ sceneToShowDetail.devices.length }}个设备)</span></h4>
          <div class="device-list">
            <div v-for="device in sceneToShowDetail.devices" :key="device.id" class="device-item">
              <div class="device-info" @click="scene_toggleDeviceSelection(device.id)">
                  <div class="device-details">
                    <div class="device-icon">
                      <i :class="getDeviceIcon(device.type)"></i>
                    </div>
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
      
      <div class="modal-actions">
        <button class="activate-btn" @click="activateScene(sceneToShowDetail.id); sceneToShowDetail = null">执行此场景</button>
        <button class="close-modal-btn" @click.stop="sceneToShowDetail = null">关闭</button>
        <!-- 保存修改 -->
         <button class="activate-btn" @click.stop="saveSceneChanges(); sceneToShowDetail = null">保存修改</button>
      </div>
    </div>
  </div>

</template>

<script>
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import DeviceCard from '@/components/devices/DeviceCard.vue'
import { ref } from 'vue'

export default {
  name: 'HomePage',
  components: {
    DeviceCard
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    // 获取状态
    const devices = computed(() => store.state.devices)
    const rooms = computed(() => store.state.rooms)
    const scenes = computed(() => store.state.scenes)
    const selectedRoom = computed(() => store.state.selectedRoom)
    const loading = computed(() => store.state.loading)
    const error = computed(() => store.state.error)

    const sceneToDelete = ref(null) // 待删除的场景
    const sceneToShowDetail = ref(null) // 待查看的场景
    // 确认删除场景
    const confirmDeleteScene = (scene) => {
      sceneToDelete.value = scene
    }
    // 删除场景
    const deleteScene = (sceneId) => {
      store.dispatch('deleteScene', sceneId)
      sceneToDelete.value = null
    }
    
    const ShowSceneDetail = (scene) => {
      console.log('查看场景详情:', scene)
      console.log('查看场景详情:', sceneToShowDetail.value)
      sceneToShowDetail.value = scene
      scene.devices.forEach(device => {
        deviceStates.value[device.id] = {
          selected: false,
          status: device.status || false,
          ...(device.type === 'light' && { brightness: device.brightness || 50 }),
          ...(device.type === 'ac' && { temperature: device.temperature || 22 }),
          ...(device.type === 'curtain' && { openPercentage: device.openPercentage || 0 })
        }
      })
    }

    // 过滤设备列表
    const filteredDevices = computed(() => {
      if (selectedRoom.value === 'all') {
        return devices.value
      }
      return devices.value.filter(
        (device) => device.room === selectedRoom.value
      )
    })

    // 生命周期钩子
    onMounted(() => {
      // 加载数据
      store.dispatch('fetchDevices')
      store.dispatch('fetchRooms')
      store.dispatch('fetchScenes')
    })

    // 方法
    const setSelectedRoom = (room) => {
      store.dispatch('setSelectedRoom', room)
    }

    const activateScene = (sceneId) => {
      
      store.dispatch('activateScene', sceneId)
    }

    const handleLogout = () => {
      store.dispatch('logout') // 调用 Vuex 的 logout action
      router.push('/login') // 跳转到登录页
    }

    //获取场景图标
    const getSceneIcon = (icon) => {
      console.log('获取场景图标:', icon)
      const iconMap = {
        home: 'fas fa-home',
        bed: 'fas fa-bed',
        sun: 'fas fa-sun',
        film: 'fas fa-film',
        utensils: 'fas fa-utensils',
        'door-open': 'fas fa-door-open'
      }
      return 'fas fa-scroll'
      // return iconMap['home']
    }

    // 获取设备图标
    const getDeviceIcon = (type) => {
      const iconMap = {
        light: 'fas fa-lightbulb',
        switch: 'fas fa-toggle-on',
        thermostat: 'fas fa-thermometer-half',
        camera: 'fas fa-video',
        sensor: 'fas fa-wifi',
        lock: 'fas fa-lock',
        outlet: 'fas fa-plug'
      };
      return iconMap[type] || 'fas fa-microchip';
    };

    // 设备状态
    const deviceStates = ref({})
    // 切换设备选择
    const scene_toggleDeviceSelection = (deviceId) => {
      deviceStates.value[deviceId].selected = !deviceStates.value[deviceId].selected
    }

    // 判断设备是否被选中
    const isDeviceSelected = (deviceId) => {
      return deviceStates.value[deviceId].selected
    }

    // 保存场景修改
    const saveSceneChanges = async () => {
      if (!sceneToShowDetail.value) return;

      try {
        console.log('保存场景修改:', sceneToShowDetail.value)
        const sceneId = sceneToShowDetail.value.id;
        const devicesToUpdate = [];
        console.log('asddsada设备状态:', deviceStates.value)
        // 收集所有修改过的设备状态
        for (const deviceId in deviceStates.value) {
          console.log('设备状态:', deviceId, deviceStates.value[deviceId])
          const deviceState = deviceStates.value[deviceId];
          // if (deviceState.selected) {
            const cur_device = devices.value.find(d => d.id === deviceId);
            devicesToUpdate.push({
              id: deviceId,
              name: cur_device.name,
              type: cur_device.type,
              room: cur_device.room,
              brand: cur_device.brand,
              status: deviceState.status,
              ...(deviceState.brightness !== undefined && { brightness: deviceState.brightness }),
              ...(deviceState.temperature !== undefined && { temperature: deviceState.temperature }),
              ...(deviceState.openPercentage !== undefined && { openPercentage: deviceState.openPercentage })
            });
          // }
        }
        
        // 调用Vuex action更新场景设备状态
        console.log('保存场景修改:', sceneId, devicesToUpdate)
        await store.dispatch('updateSceneDevices', {
          sceneId,
          devices: devicesToUpdate
        });
        
        // 关闭模态框
        // sceneToShowDetail = null;
        
        // 显示成功提示
        alert('场景修改已保存！');
        
      } catch (error) {
        console.error('保存场景失败:', error);
        alert('保存场景失败，请重试');
      }
    };



    return {
      devices,
      rooms,
      scenes,
      selectedRoom,
      loading,
      error,
      filteredDevices,
      setSelectedRoom,
      activateScene,
      handleLogout,
      getSceneIcon,
      // 
      confirmDeleteScene,
      deleteScene,
      sceneToDelete,
      sceneToShowDetail,
      ShowSceneDetail,
      getDeviceIcon,
      deviceStates,
      scene_toggleDeviceSelection,
      isDeviceSelected,
      saveSceneChanges
    }
  }
}
</script>

<style lang="scss" scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

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
    color: #666;
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

.devices-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.loading,
.error {
  padding: 20px;
  text-align: center;

  &.error {
    color: #f44336;
  }
}

.scenes-section {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #eaeaea;
}

.scenes-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.scenes-section__title {
  margin: 0;
  font-size: 22px;
  color: #333;
}

.scene-count {
  margin-left: 10px;
  color: #777;
  font-size: 14px;
}

.scenes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.scene-card {
  display: flex;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e0e6ed;
  
  &:hover {
    transform: translateY(-5px);
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
  margin-top: 10px;
  margin-bottom: 30px;
  display: inline-block;
  padding: 10px 20px;
  background: linear-gradient(to right, #2196f3, #1976d2);
  color: white;
  text-decoration: none;
  border-radius: 30px;
  font-weight: 500;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(33, 150, 243, 0.3);
  }
}



.add-device-btn {
  background: #4caf50;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 20px;
  cursor: pointer;
  text-decoration: none;
  font-size: 14px;

  &:hover {
    background: #3d8b40;
  }
}

.delete-scene-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 30px;
  height: 30px; /* 修正了原代码中 500% 的异常高度 */
  // background: rgba(244, 67, 54, 0.9);
  color: white;
  border: none;
  border-radius: 4px; /* 添加圆角 */
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 10;
  opacity: 1; /* 默认显示（原代码为 0 会隐藏按钮） */
  transform: translateY(0); /* 重置初始位置 */
  box-shadow: 0 2px 4px rgba(0,0,0,0.2); /* 添加阴影增强层次感 */

  &:hover {
    background: #d32f2f; /* 悬停加深颜色 */
    transform: scale(1.1);
    box-shadow: 0 3px 6px rgba(0,0,0,0.3); /* 悬停时阴影增强 */
  }

  &:active {
    transform: scale(0.95); /* 点击时轻微缩小 */
  }

  /* 响应式调整 */
  @media (max-width: 768px) {
    width: 26px;
    height: 26px;
    top: 6px;
    right: 6px;
  }
}

/* 删除确认对话框样式 */
.delete-confirm-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
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

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.cancel-btn {
  padding: 10px 20px;
  background: #f0f4f8;
  color: #546e7a;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.3s;
  
  &:hover {
    background: #e0e6ed;
  }
}

.confirm-delete-btn {
  padding: 10px 20px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.3s;
  
  &:hover {
    background: #d32f2f;
  }
}

.scene-detail-btn {
  // 基础样式
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
  
  // 图标样式
  i {
    font-size: 14px;
    transition: transform 0.2s;
  }
  
  // 悬浮状态
  &:hover {
    background: #1976d2;
    transform: scale(1.1);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    
    i {
      transform: scale(1.2);
    }
  }
  
  // 点击状态
  &:active {
    transform: scale(0.95);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  }
  
  // 焦点状态（无障碍访问）
  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.3);
  }
  
  // 禁用状态
  &[disabled] {
    background: #b0bec5;
    cursor: not-allowed;
    transform: none !important;
  }
  
  // 不同尺寸
  &--small {
    width: 24px;
    height: 24px;
    
    i {
      font-size: 12px;
    }
  }
  
  &--large {
    width: 36px;
    height: 36px;
    
    i {
      font-size: 16px;
    }
  }
  
  // 不同颜色变体
  &--primary {
    background: rgba(33, 150, 243, 0.9);
    
    &:hover {
      background: #1976d2;
    }
  }
  
  &--secondary {
    background: rgba(156, 39, 176, 0.9);
    
    &:hover {
      background: #7b1fa2;
    }
  }
  
  // 响应式调整
  @media (max-width: 768px) {
    width: 28px;
    height: 28px;
    top: 8px;
    right: 45px;
    
    i {
      font-size: 13px;
    }
  }
  
  @media (max-width: 480px) {
    width: 26px;
    height: 26px;
    top: 6px;
    right: 40px;
  }
  
  // 工具提示
  &::after {
    content: attr(title);
    position: absolute;
    top: -40px;
    left: 50%;
    transform: translateX(-50%);
    background: #333;
    color: white;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 12px;
    white-space: nowrap;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s;
  }
  
  &:hover::after {
    opacity: 1;
  }
}

/* 场景详情弹窗样式 */
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
    
    &.home { background: linear-gradient(135deg, #2196f3, #1976d2); }
    &.bed { background: linear-gradient(135deg, #9c27b0, #673ab7); }
    &.sun { background: linear-gradient(135deg, #ff9800, #ff5722); }
    &.film { background: linear-gradient(135deg, #f44336, #e91e63); }
    &.utensils { background: linear-gradient(135deg, #4caf50, #8bc34a); }
    &.door-open { background: linear-gradient(135deg, #607d8b, #455a64); }
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
  
  .device-item.selected & {
    background: #e3f2fd;
  }
  
  &:hover {
    background: #f1f5f9;
  }
}

.device-details {
  .device-name {
    font-weight: 500;
    color: #333;
    margin-bottom: 3px;
  }
  
  .device-room {
    font-size: 13px;
    color: #78909c;
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
</style>

