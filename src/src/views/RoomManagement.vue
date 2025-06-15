<template>
  <div class="room-management">
    <div class="room-management-header">
      <h2>房间管理</h2>
      <button @click="showCreateRoom = true" class="add-room-btn">
        <i class="fas fa-plus"></i> 添加房间
      </button>
    </div>

    <!-- 添加滚动容器 -->
    <div class="scrollable-container">
      <div class="scrollable-content">
        <div v-for="room in rooms" :key="room.id" class="room-item scrollable-item">
          <div class="room-info">
            <div v-if="!room.editing" class="room-name" @dblclick="startEditing(room)">
              {{ room.name }}
            </div>
            <div v-else class="editing-container">
              <input 
                type="text"
                v-model="room.editName"
                @keyup.enter="saveRoomName(room)"
                class="room-name-input"
                ref="roomNameInput"
              />
              <div class="edit-actions">
                <button @click="saveRoomName(room)" class="save-edit-btn">
                  <i class="fas fa-check"></i>
                </button>
                <button @click="cancelEditing(room)" class="cancel-edit-btn">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
            <div class="room-device-count">
              <i class="fas fa-microchip"></i> {{ getRoomDeviceCount(room.id) }} 个设备
            </div>
          </div>
          <div class="room-actions">
            <button @click="startEditing(room)" class="edit-btn" title="编辑名称">
              <i class="fas fa-edit"></i>
            </button>
            <button @click="confirmDeleteRoom(room)" class="delete-btn" title="删除房间">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加创建房间模态框 -->
<div v-if="showCreateRoom" class="modal">
  <div class="modal-content">
    <div class="modal-header">
      <h3>创建新房间</h3>
      <button @click="showCreateRoom = false; newRoomName = ''" class="close-modal-btn">
        <i class="fas fa-times"></i>
      </button>
    </div>
    <div class="modal-body">
      <label>房间名称</label>
      <input
        type="text"
        v-model="newRoomName"
        @keyup.enter="createRoom"
        class="modal-input"
        placeholder="输入房间名称"
        ref="newRoomInput"
        autofocus
      />
    </div>
    <div class="modal-footer">
      <button @click="showCreateRoom = false; newRoomName = ''" class="cancel-btn">取消</button>
      <button @click="createRoom" class="confirm-btn" :disabled="!newRoomName.trim()">创建</button>
    </div>
    </div>
</div>



    <!-- 删除确认模态框 -->
    <div v-if="roomToDelete" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>确认删除房间</h3>
          <button @click="roomToDelete = null" class="close-modal-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>确定要删除 <strong>"{{ roomToDelete.name }}"</strong> 吗？</p>
          <p class="warning-text">此操作将同时删除该房间中的所有设备！</p>
        </div>
        <div class="modal-footer">
          <button @click="roomToDelete = null" class="cancel-btn">取消</button>
          <button @click="deleteRoom" class="confirm-delete-btn">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, nextTick } from 'vue'

export default {
  name: 'RoomManagement',
  props: {
    rooms: {
      type: Array,
      required: true
    },
    devices: {
      type: Array,
      default: () => []
    }
  },
  emits: ['create-room', 'update-room', 'delete-room'],
  setup(props, { emit }) {
    // 保持原有脚本逻辑不变
    const showCreateRoom = ref(false)
    const newRoomName = ref('')
    const roomToDelete = ref(null)
    const roomNameInput = ref(null)
    const newRoomInput = ref(null)
    
    const getRoomDeviceCount = (roomId) => {
      console.log("房间id为：")
      console.log(roomId)
      console.log(props.devices)
      const num = props.devices.filter(device => device.room === roomId).length
      return num
    }
    
    const createRoom = async () => {
      if (newRoomName.value.trim()) {
        emit('create-room', newRoomName.value.trim())
        newRoomName.value = ''
        showCreateRoom.value = false
      }
    }
    
    const startEditing = (room) => {
      room.editing = true
      room.editName = room.name
      console.log("开始编辑房间：")
      console.log(room)
      nextTick(() => {
        if (roomNameInput.value && roomNameInput.value.length) {
          const input = roomNameInput.value.find(i => i.dataset.id === room.id)
          if (input) {
            input.focus()
            input.select()
          }
        }
      })
    }
    
    const cancelEditing = (room) => {
      room.editing = false;
    }

    const saveRoomName = (room) => {
      console.log("保存房间名称：")
      console.log(room)
      if (room.editName && room.editName.trim() !== room.name) {
        emit('update-room', {
          roomId: room.id,
          newName: room.editName.trim()
        })
      }
      room.editing = false
    }
    
    const confirmDeleteRoom = (room) => {
      roomToDelete.value = room
    }
    
    const deleteRoom = () => {
      if (roomToDelete.value) {
        emit('delete-room', roomToDelete.value.id)
        roomToDelete.value = null
      }
    }
    
    return {
      showCreateRoom,
      newRoomName,
      roomToDelete,
      roomNameInput,
      newRoomInput,
      getRoomDeviceCount,
      createRoom,
      startEditing,
      saveRoomName,
      confirmDeleteRoom,
      deleteRoom,
      cancelEditing
    }
  }
}
</script>

<style lang="scss" scoped>
.editing-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.edit-actions {
  display: flex;
  gap: 5px;
}

.save-edit-btn, .cancel-edit-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
}

.save-edit-btn {
  background: rgba(76, 175, 80, 0.1);
  color: #4caf50;
  
  &:hover {
    background: rgba(76, 175, 80, 0.2);
  }
}

.cancel-edit-btn {
  background: rgba(244, 67, 54, 0.1);
  color: #f44336;
  
  &:hover {
    background: rgba(244, 67, 54, 0.2);
  }
}
.room-management {
  /* 移除背景色、边框和阴影 */
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0;
  margin-bottom: 30px;

  .room-management-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0px;
    
    h3 {
      margin: 0;
      color: #2c3e50;
      font-size: 1.25rem;
    }
  }

  .add-room-btn {
    display: flex;
    align-items: center;
    padding: 8px 16px;
    background: linear-gradient(to right, #4caf50, #2e7d32);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s;
    
    i {
      margin-right: 8px;
    }
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
    }
  }

  /* 滚动容器样式 */
  .scrollable-container {
    width: 100%;
    overflow-x: auto;
    padding: 10px 0;
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
    gap: 15px;
    padding: 0 5px;
  }

  .scrollable-item {
    flex: 0 0 auto;
  }

  .room-item {
    display: flex;
    align-items: center;
    padding: 15px;
    background: white;
    border-radius: 8px;
    border: 1px solid #e9ecef;
    transition: all 0.3s;
    width: 360px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    
    &:hover {
      background: #f8f9fa;
      border-color: #dee2e6;
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
    }
  }

  .room-info {
    flex-grow: 1;
    min-width: 0;
  }

  .room-name {
    font-weight: 500;
    color: #333;
    font-size: 1.1rem;
    margin-bottom: 5px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    cursor: pointer;
    padding: 3px 0;
    
    &:hover {
      color: #1976d2;
    }
  }

  .room-name-input {
    width: 100%;
    padding: 5px 10px;
    border: 1px solid #2196f3;
    border-radius: 4px;
    font-size: 1rem;
    margin-bottom: 5px;
    
    &:focus {
      outline: none;
      box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.2);
    }
    flex: 1;
  }

  .room-device-count {
    display: flex;
    align-items: center;
    font-size: 0.85rem;
    color: #6c757d;
    
    i {
      margin-right: 5px;
      font-size: 0.8rem;
    }
  }

  .room-actions {
    display: flex;
    gap: 8px;
    margin-left: 10px;
  }

  .edit-btn, .delete-btn {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.2s;
    
    i {
      font-size: 14px;
    }
  }

  .edit-btn {
    background: rgba(33, 150, 243, 0.1);
    color: #1976d2;
    
    &:hover {
      background: rgba(33, 150, 243, 0.2);
    }
  }

  .delete-btn {
    background: rgba(244, 67, 54, 0.1);
    color: #d32f2f;
    
    &:hover {
      background: rgba(244, 67, 54, 0.2);
    }
  }

  /* 模态框样式保持不变 */
  .modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-content {
    background: white;
    border-radius: 12px;
    width: 100%;
    max-width: 450px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    overflow: hidden;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #e9ecef;
    
    h3 {
      margin: 0;
      font-size: 1.25rem;
      color: #2c3e50;
    }
  }

  .close-modal-btn {
    background: none;
    border: none;
    color: #6c757d;
    font-size: 1.25rem;
    cursor: pointer;
    transition: color 0.2s;
    
    &:hover {
      color: #333;
    }
  }

  .modal-body {
    padding: 20px;
    
    label {
      display: block;
      margin-bottom: 8px;
      font-weight: 500;
      color: #495057;
    }
  }

  .modal-input {
    width: 100%;
    padding: 10px 15px;
    border: 1px solid #ced4da;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.2s;
    
    &:focus {
      outline: none;
      border-color: #2196f3;
      box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.2);
    }
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    padding: 20px;
    border-top: 1px solid #e9ecef;
  }

  .cancel-btn {
    padding: 10px 20px;
    background: #f8f9fa;
    color: #495057;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
    
    &:hover {
      background: #e9ecef;
    }
  }

  .confirm-btn {
    padding: 10px 20px;
    background: #2196f3;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
    
    &:hover {
      background: #1976d2;
    }
    
    &:disabled {
      background: #90caf9;
      cursor: not-allowed;
    }
  }

  .confirm-delete-btn {
    padding: 10px 20px;
    background: #f44336;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
    
    &:hover {
      background: #d32f2f;
    }
  }

  .warning-text {
    color: #f44336;
    font-weight: 500;
    margin-top: 10px;
  }
}
</style>