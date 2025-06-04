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
        </div>
      </div>
    </div>

    <!-- 场景模式部分 -->

  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
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
    const devices = computed(() => store.state.devices)
    const rooms = computed(() => store.state.rooms)
    const scenes = computed(() => store.state.scenes)
    const selectedRoom = computed(() => store.state.selectedRoom)
    const loading = computed(() => store.state.loading)
    const error = computed(() => store.state.error)

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

    console.log('当前 filteredDevices:', filteredDevices.value)
    console.log('当前 devices:', devices.value)
    console.log('当前 selectedRoom:', selectedRoom.value)


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
</style>
