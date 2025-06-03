<template>
  <div class="home-page">
    <header class="header">
      <h1 class="header__title">智能家居控制中心</h1>

      <!-- 新加 -->
      <router-link to="/add-device" class="add-device-btn">添加设备</router-link>

     <div class="auth-info">
        yonghu
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

    <div class="scenes-section">
      <h2 class="scenes-section__title">场景模式</h2>
      <div
        v-for="scene in scenes"
        :key="scene.id"
        class="scene-card"
        @click="activateScene(scene.id)"
      >
        <h3 class="scene-card__title">{{ scene.name }}</h3>
        <p class="scene-card__desc">{{ scene.description }}</p>
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
      handleLogout
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
  margin-top: 30px;

  &__title {
    margin-bottom: 15px;
  }
}

.scene-card {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    background: #eaeaea;
  }

  &__title {
    margin: 0 0 5px 0;
  }

  &__desc {
    margin: 0;
    color: #666;
    font-size: 14px;
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
