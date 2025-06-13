<template>
  <div class="add-device-page">
    <header class="header">
      <router-link to="/" class="back-btn">
        <i class="fas fa-arrow-left"></i> 返回
      </router-link>
      <h1 class="header__title">添加新设备</h1>
      <div class="header__steps">
        <span :class="{ active: step >= 1 }">1</span>
        <span :class="{ active: step >= 2 }">2</span>
        <span :class="{ active: step >= 3 }">3</span>
      </div>
    </header>
    
    <div class="form-container">
      <!-- 设备类型选择 -->
      <transition name="fade" mode="out-in">
        <div class="form-section" v-if="step === 1" key="step1">
          <h2 class="section-title">
            <i class="fas fa-microchip"></i> 选择设备类型
          </h2>
          <div class="type-grid">
            <div 
              v-for="type in deviceTypes" 
              :key="type.value"
              class="type-card"
              :class="{ selected: selectedType === type.value }"
              @click="selectType(type.value)"
            >
              <div class="type-icon" :class="type.value">
                <i :class="getTypeIcon(type.value)"></i>
              </div>
              <span>{{ type.label }}</span>
            </div>
          </div>
          <button 
            class="next-btn"
            :disabled="!selectedType"
            @click="step = 2"
          >
            下一步 <i class="fas fa-arrow-right"></i>
          </button>
        </div>
      </transition>

      <!-- 品牌和名称 -->
      <transition name="fade" mode="out-in">
        <div class="form-section" v-if="step === 2" key="step2">
          <h2 class="section-title">
            <i class="fas fa-tag"></i> 设备详细信息
          </h2>
          
          <div class="form-group">
            <label for="device-brand">
              <i class="fas fa-copyright"></i> 品牌
            </label>
            <div class="select-wrapper">
              <select 
                id="device-brand" 
                v-model="selectedBrand" 
                class="form-select"
              >
                <option value="" disabled>请选择品牌</option>
                <option 
                  v-for="brand in filteredBrands" 
                  :key="brand.value" 
                  :value="brand.value"
                >
                  {{ brand.label }}
                </option>
              </select>
              <i class="fas fa-chevron-down"></i>
            </div>
          </div>

          <div class="form-group">
            <label for="device-name">
              <i class="fas fa-pencil-alt"></i> 设备名称
            </label>
            <div class="input-wrapper">
              <input 
                id="device-name" 
                v-model="deviceName" 
                type="text" 
                placeholder="例如: 客厅主灯"
                class="form-input"
              >
              <i class="fas fa-lightbulb"></i>
            </div>
          </div>

          <div class="form-group">
            <label for="device-room">
              <i class="fas fa-door-open"></i> 所在房间
            </label>
            <div class="select-wrapper">
              <select 
                id="device-room" 
                v-model="selectedRoom" 
                class="form-select"
              >
                <option value="" disabled>请选择房间</option>
                <option 
                  v-for="room in rooms" 
                  :key="room.id" 
                  :value="room.id"
                >
                  {{ room.name }}
                </option>
              </select>
              <i class="fas fa-chevron-down"></i>
            </div>
          </div>

          <div class="form-actions">
            <button class="back-btn" @click="step = 1">
              <i class="fas fa-arrow-left"></i> 上一步
            </button>
            <button 
              class="next-btn"
              :disabled="!canGoNext"
              @click="step = 3"
            >
              下一步 <i class="fas fa-arrow-right"></i>
            </button>
          </div>
        </div>
      </transition>

      <!-- 确认和提交 -->
      <transition name="fade" mode="out-in">
        <div class="form-section" v-if="step === 3" key="step3">
          <h2 class="section-title">
            <i class="fas fa-check-circle"></i> 确认信息
          </h2>
          
          <div class="summary-card">
            <div class="summary-item">
              <span>设备类型:</span>
              <strong>{{ getTypeLabel(selectedType) }}</strong>
            </div>
            <div class="summary-item">
              <span>品牌:</span>
              <strong>{{ getBrandLabel(selectedBrand) }}</strong>
            </div>
            <div class="summary-item">
              <span>名称:</span>
              <strong>{{ deviceName }}</strong>
            </div>
            <div class="summary-item">
              <span>房间:</span>
              <strong>{{ selectedRoom }}</strong>
            </div>
          </div>

          <div class="form-actions">
            <button class="back-btn" @click="step = 2">
              <i class="fas fa-arrow-left"></i> 上一步
            </button>
            <button 
              class="submit-btn"
              @click="submitDevice"
            >
              <i class="fas fa-plus-circle"></i> 添加设备
            </button>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'AddDevice',
  setup() {
    const store = useStore()
    const router = useRouter()

    // 表单数据
    const selectedType = ref('')
    const selectedBrand = ref('')
    const deviceName = ref('')
    const selectedRoom = ref('')
    const step = ref(1)

    // 设备类型选项
    const deviceTypes = ref([
      { value: 'light', label: '智能灯' },
      { value: 'ac', label: '空调' },
      { value: 'outlet', label: '智能插座' },
      { value: 'curtain', label: '智能窗帘' },
      { value: 'tv', label: '智能电视' },
      { value: 'monitor', label: '监控摄像头' }
    ])

    // 品牌选项 (按设备类型分类)
    const brandOptions = {
      light: [
        { value: 'philips', label: '飞利浦' },
        { value: 'xiaomi', label: '小米' },
        { value: 'ikea', label: '宜家' }
      ],
      ac: [
        { value: 'gree', label: '格力' },
        { value: 'midea', label: '美的' },
        { value: 'haier', label: '海尔' }
      ],
      outlet: [
        { value: 'xiaomi', label: '小米' },
        { value: 'tuya', label: '涂鸦' }
      ],
      curtain: [
        { value: 'aqara', label: 'Aqara' },
        { value: 'switchbot', label: 'SwitchBot' }
      ],
      tv: [
        { value: 'sony', label: '索尼' },
        { value: 'samsung', label: '三星' },
        { value: 'lg', label: 'LG' }
      ],
      monitor: [
        { value: 'hk', label: '海康威视' },
        { value: 'xiaomi', label: '小米' },
        { value: 'yingshi', label: '萤石' },
        { value: 'TL', label: 'TP-LINK' }
      ]
    }

    // 计算属性
    const filteredBrands = computed(() => {
      return selectedType.value ? brandOptions[selectedType.value] : []
    })

    const rooms = computed(() => store.state.rooms)
    
    const canSubmit = computed(() => {
      return selectedType.value && selectedBrand.value && 
             deviceName.value && selectedRoom.value
    })

    const canGoNext = computed(() => {
      return selectedBrand.value && deviceName.value && selectedRoom.value
    })

    // 方法
    const getTypeIcon = (type) => {
      const iconMap = {
        light: 'fas fa-lightbulb',
        ac: 'fas fa-snowflake',
        outlet: 'fas fa-plug',
        curtain: 'fas fa-window-maximize',
        tv: 'fas fa-tv',
        monitor: 'fas fa-video'
      }
      return iconMap[type] || 'fas fa-microchip'
    }

    const getTypeLabel = (type) => {
      const found = deviceTypes.value.find(t => t.value === type)
      return found ? found.label : ''
    }

    const getBrandLabel = (brand) => {
      if (!selectedType.value) return ''
      const found = brandOptions[selectedType.value].find(b => b.value === brand)
      return found ? found.label : ''
    }

    const selectType = (type) => {
      selectedType.value = type
      selectedBrand.value = ''
    }

    const submitDevice = () => {
      const newDevice = {
        id: Date.now().toString(),
        name: deviceName.value,
        type: selectedType.value,
        brand: selectedBrand.value,
        room: parseInt(selectedRoom.value, 10),
        status: false,
        ...(selectedType.value === 'light' && { brightness: 50 }),
        ...(selectedType.value === 'ac' && { temperature: 22 }),
        ...(selectedType.value === 'curtain' && { openPercentage: 50 })
      }

      store.dispatch('addDevice', newDevice)
      router.push('/')
    }

    // 监听步骤变化
    watch(selectedType, () => {
      if (step.value === 1 && selectedType.value) {
        step.value = 2
      }
    })

    return {
      selectedType,
      selectedBrand,
      deviceName,
      selectedRoom,
      deviceTypes,
      filteredBrands,
      rooms,
      canSubmit,
      canGoNext,
      step,
      getTypeIcon,
      getTypeLabel,
      getBrandLabel,
      selectType,
      submitDevice
    }
  }
}
</script>

<style lang="scss" scoped>
.add-device-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  background: #f8fafc;
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

.type-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.type-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 10px;
  border-radius: 12px;
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

.type-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  font-size: 24px;
  color: white;

  &.light { background: linear-gradient(135deg, #FF9800, #FFC107); }
  &.ac { background: linear-gradient(135deg, #03A9F4, #00BCD4); }
  &.outlet { background: linear-gradient(135deg, #795548, #9E9E9E); }
  &.curtain { background: linear-gradient(135deg, #4CAF50, #8BC34A); }
  &.tv { background: linear-gradient(135deg, #E91E63, #F06292); }
  &.monitor { background: linear-gradient(135deg, #9C27B0, #BA68C8); }
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
}

.select-wrapper, .input-wrapper {
  position: relative;

  i {
    position: absolute;
    right: 15px;
    top: 50%;
    transform: translateY(-50%);
    color: #90a4ae;
    pointer-events: none;
  }
}

.form-select, .form-input {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #e0e6ed;
  border-radius: 10px;
  font-size: 16px;
  transition: all 0.3s;
  appearance: none;
  background-color: white;

  &:focus {
    border-color: #2196f3;
    box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
    outline: none;
  }
}

.form-input {
  padding-right: 40px;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 40px;
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

.summary-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #e0e6ed;

  &:last-child {
    border-bottom: none;
  }

  span {
    color: #78909c;
  }

  strong {
    color: #2c3e50;
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