<template>
    <div class="add-device-page">
      <header class="header">
        <h1 class="header__title">添加新设备</h1>
        <button class="back-btn" @click="goBack">返回</button>
      </header>
      
      <div class="form-container">
        <div class="form-group">
          <label for="device-type">设备类型</label>
          <select 
            id="device-type" 
            v-model="selectedType" 
            class="form-select"
          >
            <option value="" disabled>请选择设备类型</option>
            <option 
              v-for="type in deviceTypes" 
              :key="type.value" 
              :value="type.value"
            >
               {{ type.label }}
            </option>
          </select>
        </div>
  
        <div class="form-group" v-if="selectedType">
          <label for="device-brand">品牌</label>
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
        </div>
  
        <div class="form-group" v-if="selectedBrand">
          <label for="device-name">设备名称</label>
          <input 
            id="device-name" 
            v-model="deviceName" 
            type="text" 
            placeholder="例如: 客厅主灯" 
            class="form-input"
          >
        </div>
  
        <div class="form-group" v-if="selectedType">
          <label for="device-room">所在房间</label>
          <select 
            id="device-room" 
            v-model="selectedRoom" 
            class="form-select"
          >
            <option value="" disabled>请选择房间</option>
            <option 
              v-for="room in rooms" 
              :key="room.id" 
              :value="room.name"
            >
              {{ room.name }}
            </option>
          </select>
        </div>
  
        <button 
          class="submit-btn" 
          :disabled="!canSubmit" 
          @click="submitDevice"
        >
          添加设备
        </button>
      </div>
    </div>
  </template>
  
  <script>
  import { watch,ref, computed, onMounted } from 'vue'
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
 
      // 设备类型选项
      const deviceTypes = ref([
        { value: 'light', label: '智能灯' },
        { value: 'ac', label: '空调' },
        { value: 'outlet', label: '智能插座' },
        { value: 'curtain', label: '智能窗帘' },
        { value: 'tv', label: '智能电视' },
        { value: 'monitor' , label: '监控摄像头'}
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
        monitor:[
        {value:'hk',label:'海康威视'},
        {value:'xiaomi',label:'小米'},
        {value:'yingshi',label:'萤石'},
        {value:'TL',label:'TP-LINK'}
        ],
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
  
      // 方法，返回到上一页
      const goBack = () => {
        router.go(-1)
      }
  
      const submitDevice = () => {
        const newDevice = {
          id: Date.now().toString(), // 简单生成唯一ID
          name: deviceName.value,
          type: selectedType.value,
          brand: selectedBrand.value,
          room: selectedRoom.value,
          status: false,
          // 根据设备类型设置默认值,使用 ...(条件 && { 属性 }) 语法，只有满足条件时才添加对应属性。
          ...(selectedType.value === 'light' && { brightness: 50 }),
          ...(selectedType.value === 'ac' && { temperature: 22 }),
          ...(selectedType.value === 'curtain' && { openPercentage: 50 })
        }
  
        store.dispatch('addDevice', newDevice)
        router.push('/')
      }
  
      // 生命周期钩子
      onMounted(() => {
        if (store.state.rooms.length === 0) {
          store.dispatch('fetchRooms')
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
        goBack,
        submitDevice
      }
    }
  }
  </script>
  
<style lang="scss" scoped>
  .add-device-page {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
  
    &__title {
      color: #333;
      margin: 0;
    }
  }
  
  .back-btn {
    background: #f0f0f0;
    color: #333;
    border: none;
    padding: 8px 15px;
    border-radius: 20px;
    cursor: pointer;
  
    &:hover {
      background: #e0e0e0;
    }
  }
  
  .form-container {
    max-width: 500px;
    margin: 0 auto;
    padding: 20px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  
  .form-group {
    margin-bottom: 20px;
  
    label {
      display: block;
      margin-bottom: 8px;
      font-weight: 500;
      color: #333;
    }
  }
  
  .form-select,
  .form-input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 16px;
  
    &:focus {
      outline: none;
      border-color: #2196f3;
    }
  }
  
  .submit-btn {
    width: 100%;
    padding: 12px;
    background: #2196f3;
    color: white;
    border: none;
    border-radius: 5px;
    font-size: 16px;
    cursor: pointer;
    transition: background 0.2s;
  
    &:hover {
      background: #1976d2;
    }
  
    &:disabled {
      background: #cccccc;
      cursor: not-allowed;
    }
  }
</style>