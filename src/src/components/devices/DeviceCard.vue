<template>
  <div class="device-card" :class="[
    { 'device-card--active': device.status },
    `device-card--${device.type}`
  ]">
    <!-- 编辑模式 -->
    <div v-if="isEditing" class="edit-mode">
      <div class="edit-header">
        <h4>编辑设备</h4>
        <button @click="cancelEdit" class="close-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="edit-form">
        <div class="form-group">
          <label>设备ID</label>
          <div class="device-id-display">{{ device.id }}</div>
        </div>
        
        <div class="form-group">
          <label>设备名称</label>
          <input 
            v-model="editForm.name" 
            type="text" 
            placeholder="输入设备名称"
            class="edit-input"
          />
        </div>
        
        <div class="form-group">
          <label>品牌</label>
          <input 
            v-model="editForm.brand" 
            type="text" 
            placeholder="输入品牌名称"
            class="edit-input"
          />
        </div>
        
        <div class="form-group">
          <label>房间</label>
          <!-- <select v-model="editForm.room" class="edit-select">
            <option value="客厅">客厅</option>
            <option value="卧室">卧室</option>
            <option value="厨房">厨房</option>
            <option value="书房">书房</option>
            <option value="浴室">浴室</option>
          </select> -->
          <select v-model="editForm.room" class="edit-select">
            <option v-for="room in the_rooms" 
            :value="room.id"
            :key="room.id">
            {{ room.name }}
          </option>
          </select>
        </div>
        
        <div class="edit-buttons">
          <button @click="saveEdit" class="save-btn">
            <i class="fas fa-check"></i>
            保存
          </button>
          <button @click="cancelEdit" class="cancel-btn">
            <i class="fas fa-times"></i>
            取消
          </button>
        </div>
      </div>
    </div>

    <!-- 正常显示模式 -->
    <div v-else class="normal-mode">
      <!-- 顶部操作按钮 -->
      <div class="card-actions">
        <button class="action-btn edit-btn" @click="startEdit" title="编辑">
          <i class="fas fa-edit"></i>
        </button>
        <button class="action-btn delete-btn" @click="showDeleteConfirm" title="删除">
          <i class="fas fa-trash"></i>
        </button>
      </div>

      <!-- 设备图标和状态 -->
      <div class="device-icon-section">
        <div class="device-icon-wrapper" :class="{ 'active': device.status }">
          <i :class="deviceIcon" class="device-icon"></i>
        </div>
        <div class="status-indicator" :class="{ 'active': device.status }">
          {{ device.status ? '在线' : '离线' }}
        </div>
      </div>

      <!-- 设备信息 -->
      <div class="device-info">
        <h3 class="device-name">{{ device.name }}</h3>
        <div class="device-details">
          <span class="device-room">
            <i class="fas fa-map-marker-alt"></i>
            roomid: {{ device.room }}
          </span>
          <span class="device-room">
            <i class="fas fa-map-marker-alt"></i>
            {{ cur_room_name }}
          </span>
          <span class="device-brand" v-if="device.brand">
            <i class="fas fa-tag"></i>
            {{ device.brand }}
          </span>
        </div>
        <div class="device-id">
          <i class="fas fa-barcode"></i>
          <span>ID: {{ device.id }}</span>
        </div>
      </div>

      <!-- 主要控制按钮 -->
      <button 
        class="main-toggle-btn" 
        :class="{ 'active': device.status }"
        @click="toggleDevice"
      >
        <i :class="device.status ? 'fas fa-power-off' : 'fas fa-play'"></i>
        {{ device.status ? '关闭' : '开启' }}
      </button>

      <!-- 设备参数控制 -->
      <div v-if="device.status" class="device-controls">
        <!-- 灯光亮度控制 -->
        <div v-if="device.type === 'light'" class="control-group">
          <div class="control-label">
            <i class="fas fa-sun"></i>
            <span>亮度</span>
            <span class="control-value">{{ device.extra.brightness }}%</span>
          </div>
          <div class="slider-container">
            <input 
              type="range" 
              min="0" 
              max="100" 
              :value="device.extra.brightness" 
              @input="updateBrightness"
              class="control-slider brightness-slider"
            />
          </div>
        </div>
        
        <!-- 空调温度控制 -->
        <div v-if="device.type === 'ac'" class="control-group">
          <div class="control-label">
            <i class="fas fa-thermometer-half"></i>
            <span>温度</span>
            <span class="control-value">{{ device.extra.temperature }}°C</span>
          </div>
          <div class="slider-container">
            <input 
              type="range" 
              min="16" 
              max="30" 
              :value="device.extra.temperature" 
              @input="updateTemperature"
              class="control-slider temperature-slider"
            />
          </div>
        </div>
        
        <!-- 窗帘开合度控制 -->
        <div v-if="device.type === 'curtain'" class="control-group">
          <div class="control-label">
            <i class="fas fa-arrows-alt-h"></i>
            <span>开合度</span>
            <span class="control-value">{{ device.extra.openPercentage }}%</span>
          </div>
          <div class="slider-container">
            <input 
              type="range" 
              min="0" 
              max="100" 
              :value="device.extra.openPercentage" 
              @input="updateOpenPercentage"
              class="control-slider curtain-slider"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <teleport to="body">
      <div v-if="showDeleteDialog" class="delete-confirm-dialog">
        <div class="dialog-overlay" @click="cancelDelete"></div>
        <div class="dialog-content">
          <div class="dialog-icon">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <h4>确认删除</h4>
          <p>确定要删除设备 <strong>{{ device.name }}</strong> 吗？</p>
          <p class="warning-text">此操作不可撤销</p>
          <div class="dialog-buttons">
            <button @click="confirmDelete" class="confirm-delete-btn">
              <i class="fas fa-trash"></i>
              删除
            </button>
            <button @click="cancelDelete" class="cancel-delete-btn">
              <i class="fas fa-times"></i>
              取消
            </button>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script>
import { computed, ref, reactive } from 'vue';
import { useStore } from 'vuex';

export default {
  name: 'DeviceCard',
  props: {
    device: {
      type: Object,
      required: true
    },
    rooms: {
      type: Array,
      required: true  // 如果必须传入则设为required
    }
  },

  setup(props) {
    const store = useStore();
    const showDeleteDialog = ref(false);
    const isEditing = ref(false);
    // 编辑表单数据
    const editForm = reactive({
      name: '',
      brand: '',
      room: ''
    });
    const cur_room_name = computed(() => {
      props.rooms.forEach(room => {
        console.log("当前遍历")
        console.log(room.id)
        console.log(props.device.room)
        if(room.id === props.device.room){
          console.log("找到了")
          return room.name
        }
      })
    });
    //房间列表
    const the_rooms = computed(() => {
      return props.rooms
    });
    // 设备图标
    const deviceIcon = computed(() => {
      switch (props.device.type) {
        case 'light': return 'fas fa-lightbulb';
        case 'ac': return 'fas fa-snowflake';
        case 'outlet': return 'fas fa-plug';
        case 'curtain': return 'fas fa-window-maximize';
        case 'tv': return 'fas fa-tv';
        case 'monitor': return 'fas fa-video';
        default: return 'fas fa-microchip';
      }
    });
    
    // 开始编辑
    const startEdit = () => {
      editForm.name = props.device.name;
      editForm.brand = props.device.brand || '';
      editForm.room = props.device.roomName;
      isEditing.value = true;
    };
    
    // 保存编辑
    const saveEdit = async () => {
      console.log('save edit', the_rooms);
      if (!editForm.name.trim()) {
        alert('设备名称不能为空');
        return;
      }
      
      try {
        await store.dispatch('updateDevice', {
          id: props.device.id,
          data: {
            name: editForm.name.trim(),
            brand: editForm.brand.trim(),
            room: editForm.room
          }
        });
        isEditing.value = false;
      } catch (error) {
        alert('保存失败，请重试');
      }
    };
    
    // 取消编辑
    const cancelEdit = () => {
      isEditing.value = false;
      editForm.name = '';
      editForm.brand = '';
      editForm.room = '';
    };
    
    // 显示删除确认对话框
    const showDeleteConfirm = () => {
      showDeleteDialog.value = true;
    };

    // 确认删除
    const confirmDelete = async () => {
      try {
        await store.dispatch('deleteDevice', props.device.id);
        showDeleteDialog.value = false;
      } catch (error) {
        alert('删除失败，请重试');
      }
    };

    // 取消删除
    const cancelDelete = () => {
      showDeleteDialog.value = false;
    };
    
    // 开关设备
    const toggleDevice = () => {
      console.log('toggle device', props);
      console.log('device ', props.device);
      store.dispatch('toggleDevice', { 
        id: props.device.id, 
        status: !props.device.status 
      });
    };
    
    // 更新亮度
    const updateBrightness = (event) => {
      store.dispatch('updateDevice', {
        id: props.device.id,
        data: { extra: {brightness: parseInt(event.target.value)} }
      });
    };
    
    // 更新温度
    const updateTemperature = (event) => {
      store.dispatch('updateDevice', {
        id: props.device.id,
        data: { extra: {temperature: parseInt(event.target.value)} }
      });
    };
    
    // 更新窗帘开合度
    const updateOpenPercentage = (event) => {
      store.dispatch('updateDevice', {
        id: props.device.id,
        data: {extra: {openPercentage: parseInt(event.target.value)} }
      });
    };
    
    return {
      the_rooms,
      deviceIcon,
      toggleDevice,
      updateBrightness,
      updateTemperature,
      updateOpenPercentage,
      showDeleteDialog,
      showDeleteConfirm,
      confirmDelete,
      cancelDelete,
      isEditing,
      editForm,
      startEdit,
      saveEdit,
      cancelEdit,
      cur_room_name
    };
  }
}
</script>

<style lang="scss" scoped>
// 设备类型配色方案
$device-colors: (
  light: (
    primary: #ffc107,
    secondary: #fff9c4,
    accent: #ff8f00,
    gradient: linear-gradient(135deg, #ffc107, #ff8f00)
  ),
  ac: (
    primary: #2196f3,
    secondary: #e3f2fd,
    accent: #0d47a1,
    gradient: linear-gradient(135deg, #2196f3, #1976d2)
  ),
  outlet: (
    primary: #4caf50,
    secondary: #e8f5e9,
    accent: #2e7d32,
    gradient: linear-gradient(135deg, #4caf50, #388e3c)
  ),
  curtain: (
    primary: #795548,
    secondary: #efebe9,
    accent: #5d4037,
    gradient: linear-gradient(135deg, #795548, #6d4c41)
  ),
  tv: (
    primary: #9c27b0,
    secondary: #f3e5f5,
    accent: #6a1b9a,
    gradient: linear-gradient(135deg, #9c27b0, #7b1fa2)
  ),
  monitor: (
    primary: #607d8b,
    secondary: #eceff1,
    accent: #455a64,
    gradient: linear-gradient(135deg, #607d8b, #546e7a)
  )
);

.device-card {
  background: linear-gradient(145deg, #ffffff, #f8f9fa);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.08),
    0 2px 8px rgba(0, 0, 0, 0.04);
  margin-bottom: 20px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #667eea, #764ba2);
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  // 为每种设备类型设置不同的配色
  @each $type, $colors in $device-colors {
    &.device-card--#{$type} {
      &::before {
        background: map-get($colors, gradient);
      }
      
      &:hover::before,
      &.device-card--active::before {
        opacity: 1;
      }
      
      &.device-card--active {
        background: linear-gradient(145deg, #{map-get($colors, secondary)}, #ffffff);
        border-color: rgba(map-get($colors, primary), 0.2);
      }
      
      .device-icon-wrapper.active {
        background: map-get($colors, gradient) !important;
        
        &::before {
          background: map-get($colors, gradient);
        }
      }
      
      .status-indicator.active {
        background: map-get($colors, gradient) !important;
      }
      
      .main-toggle-btn.active {
        background: map-get($colors, gradient) !important;
        border-color: map-get($colors, primary);
        
        &:hover {
          background: map-get($colors, accent) !important;
        }
      }
      
      .control-slider {
        &::-webkit-slider-thumb {
          background: map-get($colors, gradient) !important;
        }
        
        &::-moz-range-thumb {
          background: map-get($colors, primary) !important;
        }
      }
      
      .device-brand {
        color: map-get($colors, accent);
      }
    }
  }

  &:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 
      0 20px 40px rgba(0, 0, 0, 0.15),
      0 8px 16px rgba(0, 0, 0, 0.08);

    &::before {
      opacity: 1;
    }
  }

  // 编辑模式样式
  .edit-mode {
    .edit-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 2px solid #f0f0f0;

      h4 {
        margin: 0;
        color: #333;
        font-size: 18px;
        font-weight: 600;
      }

      .close-btn {
        background: #f5f5f5;
        border: none;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        cursor: pointer;
        color: #666;
        transition: all 0.2s ease;

        &:hover {
          background: #e0e0e0;
          color: #333;
        }
      }
    }

    .edit-form {
      .form-group {
        margin-bottom: 16px;

        label {
          display: block;
          margin-bottom: 6px;
          font-weight: 500;
          color: #555;
          font-size: 14px;
        }

        .device-id-display {
          padding: 12px 16px;
          background: #f8f9fa;
          border: 2px solid #e9ecef;
          border-radius: 10px;
          font-family: 'Courier New', monospace;
          font-size: 13px;
          color: #6c757d;
          font-weight: 500;
        }

        .edit-input,
        .edit-select {
          width: 100%;
          padding: 12px 16px;
          border: 2px solid #e1e5e9;
          border-radius: 10px;
          font-size: 14px;
          transition: border-color 0.3s ease;
          background: #fafafa;

          &:focus {
            outline: none;
            border-color: #667eea;
            background: #fff;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
          }
        }
      }

      .edit-buttons {
        display: flex;
        gap: 12px;
        margin-top: 20px;

        button {
          flex: 1;
          padding: 12px 16px;
          border: none;
          border-radius: 10px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;

          i {
            font-size: 14px;
          }
        }

        .save-btn {
          background: linear-gradient(135deg, #4caf50, #8bc34a);
          color: white;

          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
          }
        }

        .cancel-btn {
          background: #f5f5f5;
          color: #666;

          &:hover {
            background: #e0e0e0;
            color: #333;
          }
        }
      }
    }
  }

  // 正常模式样式
  .normal-mode {
    .card-actions {
      position: absolute;
      top: 16px;
      right: 16px;
      display: flex;
      gap: 8px;
      opacity: 0;
      transition: opacity 0.3s ease;

      .action-btn {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        transition: all 0.2s ease;

        &.edit-btn {
          background: rgba(102, 126, 234, 0.1);
          color: #667eea;

          &:hover {
            background: #667eea;
            color: white;
            transform: scale(1.1);
          }
        }

        &.delete-btn {
          background: rgba(255, 82, 82, 0.1);
          color: #ff5252;

          &:hover {
            background: #ff5252;
            color: white;
            transform: scale(1.1);
          }
        }
      }
    }

    &:hover .card-actions {
      opacity: 1;
    }

    .device-icon-section {
      text-align: center;
      margin-bottom: 20px;

      .device-icon-wrapper {
        width: 80px;
        height: 80px;
        margin: 0 auto 12px;
        border-radius: 50%;
        background: linear-gradient(145deg, #f0f0f0, #e0e0e0);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        position: relative;

        &::before {
          content: '';
          position: absolute;
          inset: -3px;
          border-radius: 50%;
          background: linear-gradient(45deg, #667eea, #764ba2);
          opacity: 0;
          transition: opacity 0.3s ease;
          z-index: -1;
        }

        &.active {
          color: white;
          animation: pulse 2s infinite;

          &::before {
            opacity: 1;
          }
        }

        .device-icon {
          font-size: 32px;
          color: #666;
          transition: all 0.3s ease;
        }

        &.active .device-icon {
          color: white;
        }
      }

      .status-indicator {
        font-size: 12px;
        color: #999;
        background: #f5f5f5;
        padding: 4px 12px;
        border-radius: 12px;
        display: inline-block;
        font-weight: 500;
        transition: all 0.3s ease;

        &.active {
          color: white;
        }
      }
    }

    .device-info {
      text-align: center;
      margin-bottom: 20px;

      .device-name {
        margin: 0 0 8px 0;
        font-size: 18px;
        font-weight: 600;
        color: #333;
        line-height: 1.2;
      }

      .device-details {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-bottom: 8px;
        flex-wrap: wrap;

        .device-room,
        .device-brand {
          font-size: 12px;
          padding: 4px 10px;
          border-radius: 10px;
          display: inline-flex;
          align-items: center;
          gap: 4px;

          i {
            font-size: 10px;
          }
        }

        .device-room {
          background: rgba(102, 126, 234, 0.1);
          color: #667eea;
        }

        .device-brand {
          background: rgba(255, 152, 0, 0.1);
          color: #ff9800;
          font-weight: 500;
        }
      }

      .device-id {
        font-size: 11px;
        color: #999;
        background: #f8f9fa;
        padding: 4px 8px;
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-family: 'Courier New', monospace;

        i {
          font-size: 10px;
        }
      }
    }

    .main-toggle-btn {
      width: 100%;
      padding: 12px 20px;
      border: 2px solid #e1e5e9;
      background: #fafafa;
      color: #666;
      border-radius: 12px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      margin-bottom: 16px;

      &:hover {
        background: #f0f0f0;
        border-color: #d0d0d0;
        transform: translateY(-1px);
      }

      &.active {
        color: white;

        &:hover {
          transform: translateY(-2px);
        }
      }

      i {
        font-size: 16px;
      }
    }

    .device-controls {
      .control-group {
        margin-bottom: 16px;

        .control-label {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 8px;
          font-size: 13px;
          color: #666;

          span:first-of-type {
            display: flex;
            align-items: center;
            gap: 6px;
          }

          .control-value {
            font-weight: 600;
            color: #333;
          }
        }

        .slider-container {
          position: relative;

          .control-slider {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: #e1e5e9;
            outline: none;
            cursor: pointer;
            -webkit-appearance: none;
            appearance: none;

            &::-webkit-slider-thumb {
              -webkit-appearance: none;
              width: 18px;
              height: 18px;
              border-radius: 50%;
              cursor: pointer;
              box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
              transition: all 0.2s ease;

              &:hover {
                transform: scale(1.2);
              }
            }

            &::-moz-range-thumb {
              width: 18px;
              height: 18px;
              border-radius: 50%;
              cursor: pointer;
              border: none;
              box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
            }
          }
        }
      }
    }
  }
}

// 删除确认对话框样式
.delete-confirm-dialog {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;

  .dialog-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
  }

  .dialog-content {
    position: relative;
    background: white;
    padding: 32px;
    border-radius: 20px;
    width: 100%;
    max-width: 400px;
    text-align: center;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
    animation: dialogSlideIn 0.3s ease-out;

    .dialog-icon {
      width: 64px;
      height: 64px;
      margin: 0 auto 16px;
      border-radius: 50%;
      background: linear-gradient(135deg, #ff5252, #f44336);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 24px;
    }

    h4 {
      margin: 0 0 12px 0;
      font-size: 20px;
      color: #333;
      font-weight: 600;
    }

    p {
      margin: 0 0 8px 0;
      color: #666;
      line-height: 1.5;

      strong {
        color: #333;
      }
    }

    .warning-text {
      color: #ff5252;
      font-size: 13px;
      font-weight: 500;
      margin-bottom: 24px;
    }

    .dialog-buttons {
      display: flex;
      gap: 12px;

      button {
        flex: 1;
        padding: 12px 20px;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;

        i {
          font-size: 14px;
        }
      }

      .confirm-delete-btn {
        background: linear-gradient(135deg, #ff5252, #f44336);
        color: white;

        &:hover {
          background: linear-gradient(135deg, #f44336, #d32f2f);
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(255, 82, 82, 0.3);
        }
      }

      .cancel-delete-btn {
        background: #f5f5f5;
        color: #666;

        &:hover {
          background: #e0e0e0;
          color: #333;
        }
      }
    }
  }
}

// 动画
@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.4);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(76, 175, 80, 0);
  }
}

@keyframes dialogSlideIn {
  from {
    opacity: 0;
    transform: scale(0.8) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .device-card {
    padding: 20px;
    margin-bottom: 16px;

    .normal-mode {
      .device-icon-section .device-icon-wrapper {
        width: 64px;
        height: 64px;

        .device-icon {
          font-size: 24px;
        }
      }

      .device-info .device-name {
        font-size: 16px;
      }

      .device-details {
        flex-direction: column;
        align-items: center;
      }
    }

    .edit-mode .edit-form .edit-buttons {
      flex-direction: column;

      button {
        padding: 14px 16px;
      }
    }
  }

  .delete-confirm-dialog .dialog-content {
    padding: 24px;
    margin: 16px;

    .dialog-buttons {
      flex-direction: column;
    }
  }
}
</style>