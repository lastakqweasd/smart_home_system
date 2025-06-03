<template>
  <div class="device-card" :class="{ 'device-card--active': device.status }">

    <!-- 删除按钮（右上角） -->
    <button class="device-card__delete-btn" @click="showDeleteConfirm">
      <i class="fas fa-trash"></i>
    </button>

    <div class="device-card__header">
      <h3 class="device-card__title">{{ device.name }}</h3>
      <span class="device-card__room">{{ device.room }}</span>
    </div>
    
    <div class="device-card__status">
      <div class="device-card__icon" :class="{ 'active': device.status }">
        <i :class="deviceIcon"></i>
      </div>
      <button 
        class="device-card__toggle-btn" 
        :class="{ 'active': device.status }"
        @click="toggleDevice"
      >
        {{ device.status ? '开启' : '关闭' }}
      </button>
    </div>
    
    <!-- 灯光亮度控制 -->
    <div v-if="device.type === 'light' && device.status" class="device-card__control">
      <small>亮度: {{ device.brightness }}%</small>
      <input 
        type="range" 
        min="0" 
        max="100" 
        :value="device.brightness" 
        @input="updateBrightness"
        class="device-card__slider"
      />
    </div>
    
    <!-- 空调温度控制 -->
    <div v-if="device.type === 'ac' && device.status" class="device-card__control">
      <small>温度: {{ device.temperature }}°C</small>
      <input 
        type="range" 
        min="16" 
        max="30" 
        :value="device.temperature" 
        @input="updateTemperature"
        class="device-card__slider"
      />
    </div>
    
    
    <!-- 窗帘开合度控制 -->
    <div v-if="device.type === 'curtain'&& device.status" class="device-card__control">
      <small>开合度: {{ device.openPercentage }}%</small>
      <input 
        type="range" 
        min="0" 
        max="100" 
        :value="device.openPercentage" 
        @input="updateOpenPercentage"
        class="device-card__slider"
      />
    </div>

    <!-- 删除确认对话框 -->
    <!-- 将确认对话框移到卡片外部，放在body层级 -->
  <teleport to="body">
    <div v-if="showDeleteDialog" class="delete-confirm-dialog">
      <div class="dialog-content">
        <p>确定要删除 {{ device.name }} 吗？</p>
        <div class="dialog-buttons">
          <button @click="confirmDelete" class="confirm-btn">确定</button>
          <button @click="cancelDelete" class="cancel-btn">取消</button>
        </div>
      </div>
    </div>
  </teleport>

  </div>
</template>

<script>
import { computed,ref } from 'vue';
import { useStore } from 'vuex';

export default {
  name: 'DeviceCard',
  props: {
    device: {
      type: Object,
      required: true
    }
  },

  setup(props) {
    const store = useStore();
    const showDeleteDialog=ref(false);
    
    // 显示删除确认对话框
    const showDeleteConfirm = () => {
      showDeleteDialog.value = true;
    };

    // 确认删除
    const confirmDelete = () => {
      store.dispatch('deleteDevice', props.device.id);
      showDeleteDialog.value = false;
    };

    // 取消删除
    const cancelDelete = () => {
      showDeleteDialog.value = false;
    };

    // 设备图标
    const deviceIcon = computed(() => {
      switch (props.device.type) {
        case 'light': return 'fas fa-lightbulb';
        case 'ac': return 'fas fa-snowflake';
        case 'outlet': return 'fas fa-plug';
        case 'curtain': return 'fas fa-window-maximize';
        case 'tv': return 'fas fa-tv';
        case 'monitor': return 'fas fa-video';
        default: return 'fas fa-lightbulb';
      }
    });
    
    // 开关设备
    const toggleDevice = () => {
      store.dispatch('toggleDevice', { 
        id: props.device.id, 
        status: !props.device.status 
      });
    };
    
    // 更新亮度
    const updateBrightness = (event) => {
      store.dispatch('updateDevice', {
        id: props.device.id,
        data: { brightness: parseInt(event.target.value) }
      });
    };
    
    // 更新温度
    const updateTemperature = (event) => {
      store.dispatch('updateDevice', {
        id: props.device.id,
        data: { temperature: parseInt(event.target.value) }
      });
    };
    
    // 更新窗帘开合度
    const updateOpenPercentage = (event) => {
      store.dispatch('updateDevice', {
        id: props.device.id,
        data: { openPercentage: parseInt(event.target.value) }
      });
    };
    
    return {
      deviceIcon,
      toggleDevice,
      updateBrightness,
      updateTemperature,
      updateOpenPercentage,
      showDeleteDialog,
      showDeleteConfirm,
      confirmDelete,
      cancelDelete
    };
  }
}
</script>

<style lang="scss" scoped>
.device-card {
  // position: relative; /* 为绝对定位的删除按钮提供参照 */
  background: white;
  border-radius: 10px;
  padding: 15px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 15px;
  transition: all 0.3s ease;
  
  &__delete-btn {
    position: absolute;
    bottom: -1px;
    right: 10px;
    background: transparent;
    border: none;
    color: #ff5252;
    cursor: pointer;
    font-size: 14px;
    padding: 5px;
    transition: all 0.2s;
    
    &:hover {
      color: #ff0000;
      transform: scale(1.1);
    }
  }

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }
  
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }
  
  &__title {
    margin: 0;
    font-size: 16px;
    color: #333;
  }
  
  &__room {
    font-size: 12px;
    color: #666;
    background: #f0f0f0;
    padding: 3px 8px;
    border-radius: 10px;
  }
  
  &__status {
    display: flex;
    align-items: center;
    margin: 10px 0;
  }
  
  &__icon {
    font-size: 24px;
    color: #ccc;
    margin-right: 15px;
    
    &.active {
      color: #4caf50;
    }
  }
  
  &__toggle-btn {
    background: #f0f0f0;
    color: #333;
    border: none;
    padding: 8px 15px;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      background: #e0e0e0;
    }
    
    &.active {
      background: #4caf50;
      color: white;
      
      &:hover {
        background: #3d8b40;
      }
    }
  }
  
  &__control {
    margin-top: 10px;
    
    small {
      display: block;
      margin-bottom: 5px;
      color: #666;
    }
  }
  
  &__slider {
    width: 100%;
    cursor: pointer;
  }
}

/* 删除确认对话框样式 */
.delete-confirm-dialog {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  
  .dialog-content {
    background: white;
    padding: 20px;
    border-radius: 8px;
    width: 300px;
    text-align: center;
    
    p {
      margin-bottom: 20px;
      font-size: 16px;
    }
  }
  
  .dialog-buttons {
    display: flex;
    justify-content: center;
    gap: 15px;
    
    button {
      padding: 8px 20px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;
    }
    
    .confirm-btn {
      background: #ff5252;
      color: white;
      
      &:hover {
        background: #ff0000;
      }
    }
    
    .cancel-btn {
      background: #e0e0e0;
      
      &:hover {
        background: #bdbdbd;
      }
    }
  }
}
</style>