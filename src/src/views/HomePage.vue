<template>
  <div class="home-page">
    <header class="header">
      <h1 class="header__title">智能家居控制中心</h1>
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
        :class="{ active: selectedRoom === room.name }"
        @click="setSelectedRoom(room.name)"
      >
        {{ room.name }}
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
            class="scrollable-item"
          />
        </div>
      </div>
    </div>

    <div class="scenes-section">
      <div class="scenes-header">
        <h2 class="scenes-section__title">场景模式</h2>
        <!-- <div class="scene-count">({{ scenes.length }}个场景)</div> -->
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
                <i class="fas fa-microchip"></i> {{scene.devices.length}} 个设备
              </div>
            </div>
            <button 
              class="delete-scene-btn" 
              title="删除"
              @click.stop="confirmDeleteScene(scene)"
            >
              <i class="fas fa-trash-alt"></i>
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
          <button class="confirm-delete-btn" @click.stop="deleteScene(sceneToDelete.id)">删除</button>
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

export default {
  name: 'HomePage',
  components: {
    DeviceCard
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

    // 过滤设备列表
    const filteredDevices = computed(() => {
      if (!Array.isArray(devices.value)) return []
      
      if (selectedRoom.value === 'all') {
        return devices.value
      }
      return devices.value.filter(
        (device) => device?.room === selectedRoom.value
      ) || []
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
      setSelectedRoom,
      activateScene,
      confirmDeleteScene,
      deleteScene,
      handleLogout,
      getSceneIcon
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

/* 新增滑动容器样式 */
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

/* 设备卡片样式 */
.device-card {
  margin: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-3px);
  }
}

/* 场景卡片样式 */
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

  @media (max-width: 768px) {
    width: 26px;
    height: 26px;
    top: 6px;
    right: 6px;
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

.loading,
.error {
  padding: 20px;
  text-align: center;

  &.error {
    color: #f44336;
  }
}
</style>