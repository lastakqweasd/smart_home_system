import { createStore } from 'vuex'
import { api } from '@/services/api'

export default createStore({
  state: {
    devices: [],
    rooms: [],
    scenes: [],
    selectedRoom: 'all',
    loading: false,
    error: null,
    user: null,
  },
  mutations: {
    SET_SUCCESS(state, message) {
      state.successMessage = message;
    },
    SET_DEVICES(state, devices) {
      state.devices = devices
    },
    SET_ROOMS(state, rooms) {
      state.rooms = rooms
    },
    SET_SCENES(state, scenes) {
      state.scenes = scenes
    },
    SET_SELECTED_ROOM(state, room) {
      state.selectedRoom = room
    },
    UPDATE_DEVICE(state, updatedDevice) {
      console.log(updatedDevice)
      const index = state.devices.findIndex(
        (device) => device.id === updatedDevice.id
      )
      if (index !== -1) {
        state.devices[index] = { ...state.devices[index], ...updatedDevice }
      }
    },
    SET_LOADING(state, status) {
      state.loading = status
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    ADD_DEVICE(state, device) {
      state.devices.push(device)
    },
    REMOVE_DEVICE(state, deviceId) {
      state.devices = state.devices.filter(device => device.id !== deviceId);
    },
    SET_USER(state, user) {
      state.user = user
    },
    CLEAR_USER(state) {
      state.user = null
    },
    ADD_SCENE(state, scene) {
      console.log(scene)
      console.log(state.scenes)
      state.scenes.push(scene)
    },

    //删除场景
    REMOVE_SCENE(state, sceneId) {
      state.scenes = state.scenes.filter(scene => scene.id !== sceneId)
    },

    //关闭所有设备
    RESET_DEVICES(state) {
      state.devices = state.devices.map(device => ({...device, status: false}))
      state.devices.forEach(device => {
        api.updateDevice(device.id, { status: false })
      })
    },

    //更新设备
    UPDATE_SCENE_DEVICES(state, { sceneId, devices }) {
      const scene = state.scenes.find(s => s.id === sceneId);
      if (scene) {
        scene.devices = devices;
      }
    },
    ADD_ROOM(state, room) {
      state.rooms.push(room);
    },
    REMOVE_ROOM(state, roomId) {
      state.rooms = state.rooms.filter(room => room.id !== roomId);
      state.devices = state.devices.filter(device => device.roomId !== roomId);
    },
    //关闭所有设备
    RESET_DEVICES(state) {
      state.devices = state.devices.map(device => ({...device, status: false}))
      state.devices.forEach(device => {
        api.updateDevice(device.id, { status: false })
      })
    },
    UPDATE_ROOM_NAME(state, { roomId, newName }) {
      const room = state.rooms.find(r => r.id === roomId);
      if (room) {
        room.name = newName;
        state.devices
          .filter(device => device.roomId === roomId)
          .forEach(device => {
            device.roomName = newName;
          });
      }
    },
  },
  actions: {
    // 删除设备 - 添加用户验证
    async deleteDevice({ commit, state }, deviceId) {
      try {
        await api.delDevice(deviceId)
        commit('REMOVE_DEVICE', deviceId);
        return true;
      } catch (error) {
        console.error('删除设备失败:', error);
        return false;
      }
    },

    // 添加设备 - 关联当前用户
    async addDevice({ commit, state }, device) {
      commit('SET_LOADING', true);
      try {
        const userId = state.user?.id
        if (!userId) {
          commit('SET_ERROR', '请先登录')
          return false
        }
        
        // 添加用户ID到设备数据
        const deviceWithUser = { ...device, userId }
        const response = await api.postDevice(deviceWithUser)
        commit('ADD_DEVICE', response.data);
        return true;
      } catch (error) {
        commit('SET_ERROR', '添加设备失败');
        console.error(error);
        return false;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    // 获取设备 - 只获取当前用户的设备
    async fetchDevices({ commit, state }) {
      commit('SET_LOADING', true)
      try {
        const userId = state.user?.id
        if (!userId) {
          commit('SET_DEVICES', []) // 未登录时显示空设备列表
          return
        }
        
        const response = await api.getAllDevices()
        // 过滤出当前用户的设备
        const userDevices = response.data.filter(device => device.userId === userId)
        commit('SET_DEVICES', userDevices)
      } catch (error) {
        commit('SET_ERROR', '获取设备列表失败')
        console.error(error)
      } finally {
        commit('SET_LOADING', false)
      }
    },

    // 获取房间 - 保持所有用户共享
    async fetchRooms({ commit }) {
      try {
        const response = await api.getRooms()
        commit('SET_ROOMS', response.data)
      } catch (error) {
        commit('SET_ERROR', '获取房间列表失败')
        console.error(error)
      }
    },

    // 获取场景 - 只获取当前用户的场景
    async fetchScenes({ commit, state }) {
      try {
        const userId = state.user?.id
        if (!userId) {
          commit('SET_SCENES', []) // 未登录时显示空场景列表
          return
        }
        
        const response = await api.getScenes()
        // 过滤出当前用户的场景
        const userScenes = response.data.filter(scene => scene.userId === userId)
        commit('SET_SCENES', userScenes)
      } catch (error) {
        commit('SET_ERROR', '获取场景列表失败')
        console.error(error)
      }
    },

    setSelectedRoom({ commit }, room) {
      commit('SET_SELECTED_ROOM', room)
    },

    async createRoom({ commit }, roomData) {
      commit('SET_LOADING', true);
      try {
        const newRoom = {
          id: Date.now().toString(),
          name: roomData.name,
        };
        
        // 调用API创建房间
        const response = await api.createRoom(newRoom);
        commit('ADD_ROOM', response.data);
        return true;
      } catch (error) {
        commit('SET_ERROR', '创建房间失败');
        console.error(error);
        return false;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    async deleteRoom({ commit, state }, roomId) {
      commit('SET_LOADING', true);
      try {
        // 删除该房间的所有设备
        const roomDevices = state.devices.filter(d => d.roomId === roomId);
        await Promise.all(roomDevices.map(device => 
          api.delDevice(device.id)
        ));
        
        // 删除房间本身
        await api.delRoom(roomId);
        
        // 提交 mutation 更新状态
        commit('REMOVE_ROOM', roomId);
        return true;
      } catch (error) {
        commit('SET_ERROR', '删除房间失败');
        console.error(error);
        return false;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    async updateRoom({ commit }, payload) {
    commit('SET_LOADING', true);
    try {
      const { roomId, newName } = payload;
      // 调用 API 更新房间
      await api.updateRoom(roomId, { name: newName });
      // 提交 mutation 更新前端状态
      commit('UPDATE_ROOM_NAME', { roomId, newName });
      return true;
    } catch (error) {
      commit('SET_ERROR', '更新房间名称失败');
      console.error(error);
      return false;
    } finally {
      commit('SET_LOADING', false);
    }
  },

    async toggleDevice({ commit }, { id, status }) {
      try {
        console.log(id)
        console.log({status})
        if (status === undefined) {
          console.error(`toggleDevice: Invalid status for device ${id}`);
          return;
        }
        const response = await api.updateDevice(id, { status })
        console.log(response)
        const updatedDevice = response.data
        commit('UPDATE_DEVICE', updatedDevice)
      } catch (error) {
        commit('SET_ERROR', '设备状态更新失败')
        console.error(error)
      }
    },

    async updateDevice({ commit }, { id, data }) {
      try {
        const response = await api.updateDevice(id, data)
        commit('UPDATE_DEVICE', response.data)
      } catch (error) {
        commit('SET_ERROR', '设备更新失败')
        console.error(error)
      }
    },

    async activateScene({ commit, dispatch, state }, sceneId) {
      commit('SET_LOADING', true)
      try {
        commit('RESET_DEVICES')
        console.log(this.state.devices)
        await api.activateScene(sceneId)
        // 重新获取设备状态
        dispatch('fetchDevices')
      } catch (error) {
        commit('SET_ERROR', '场景激活失败')
        console.error(error)
      } finally {
        commit('SET_LOADING', false)
      }
    },

    // 登录 - 登录成功后自动获取用户数据
    // async login({ commit, dispatch }, credentials) {
    //   try {
    //     const response = await api.getUsers({
    //       name: credentials.username,
    //       password: credentials.password
    //     })
        
    //     if (response.data.length > 0) {
    //       commit('SET_USER', response.data[0]);
          
    //       // 登录成功后立即获取该用户的数据
    //       await Promise.all([
    //         dispatch('fetchDevices'),
    //         dispatch('fetchRooms'), 
    //         dispatch('fetchScenes')
    //       ]);
          
    //       return true
    //     }
    //     return false
    //   } catch (error) {
    //     console.error('登录失败:', error)
    //     return false
    //   }
    // },
    // 登录 - 登录成功后自动获取用户数据
    async login({ commit, dispatch }, credentials) {
      try {
        console.log('开始登录...', credentials);
        const response = await api.login({
          name: credentials.username,
          password: credentials.password
        });
        const data = await response.json();
        console.log('登录成功sdda:', data);
        if (data.success) {
          console.log("jinxl");
          commit('SET_USER', data.user);
          // 登录成功后立即获取该用户的数据
          await Promise.all([
            dispatch('fetchDevices'),
            dispatch('fetchRooms'), 
            dispatch('fetchScenes')
          ]);
          console.log("qwewqe");
          console.log('登录成功:', response.json())
          return true
        }
        return false
      } 
      catch (error) {
        console.error('登录失败:', error)
        return false
      }
    },

    // 注销 - 清空用户相关数据
    logout({ commit }) {
      commit('CLEAR_USER')
      commit('SET_DEVICES', [])
      commit('SET_SCENES', [])
      // 房间保留，因为是共享的
      commit('SET_SELECTED_ROOM', 'all')
    },

    // async register({ commit, dispatch }, userData) {
    //   commit('SET_LOADING', true);
    //   commit('SET_ERROR', null);
      
    //   try {
    //     console.log('开始注册...', userData);
        
    //     const existingUsers = await api.getUsers({ name: userData.username });
    //     console.log('现有用户查询结果:', existingUsers);
        
    //     if (existingUsers.data.length > 0) {
    //       commit('SET_ERROR', '用户名已存在');
    //       return false;
    //     }
        
    //     const newUser = {
    //       id: Date.now().toString(),
    //       name: userData.username,
    //       password: userData.password,
    //       role: 'member',
    //       permissions: ['read', 'write']
    //     };
        
    //     if (userData.email) {
    //       newUser.email = userData.email;
    //     }
        
    //     console.log('准备创建用户:', newUser);
        
    //     const response = await api.createUser(newUser);
    //     console.log('创建用户成功:', response.data);
        
    //     commit('SET_USER', response.data);
        
    //     // 注册成功后获取数据
    //     await Promise.all([
    //       dispatch('fetchDevices'),
    //       dispatch('fetchRooms'), 
    //       dispatch('fetchScenes')
    //     ]);
        
    //     return true;
    //   } catch (error) {
    //     console.error('注册失败详情:', error);
    //     commit('SET_ERROR', '注册失败，请重试');
    //     return false;
    //   } finally {
    //     commit('SET_LOADING', false);
    //   }
    // },

    async register({ commit, dispatch }, userData) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      commit('SET_SUCCESS', null); // 新增成功状态
    
      // 前端验证（根据截图1的需求）
      if (!/.*\d.*/.test(userData.username)) {
        commit('SET_ERROR', '用户名必须包含数字');
        commit('SET_LOADING', false);
        return false;
      }
    
      try {
        const response = await api.createUser({
          username: userData.username,
          email: userData.email,
          phone: userData.phone,
          nickname: userData.nickname,
          password: userData.password,
          password_confirm: userData.password_confirm
        });
    
        // 明确处理成功响应（根据您的后端API结构）
        if (response.data?.success) {
          commit('SET_USER', response.data.user);
          commit('SET_SUCCESS', response.data.message || '注册成功');
          
          // 初始化数据
          await Promise.all([
            dispatch('fetchDevices'),
            dispatch('fetchRooms'),
            dispatch('fetchScenes')
          ]);
          
          return true;
        } else {
          // 处理API返回的非预期成功状态
          commit('SET_ERROR', response.data?.errors || '注册失败');
          return false;
        }
      } catch (error) {
        // 增强错误处理
        const errorData = error.response?.data;
        const errorMsg = errorData?.detail || 
                        errorData?.message || 
                        errorData?.errors?.username?.[0] || 
                        '注册失败，请重试';
        commit('SET_ERROR', errorMsg);
        return false;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    // 创建场景 - 关联当前用户
    async createScene({ commit, state }, scene) {
      commit('SET_LOADING', true);
      try {
        const userId = state.user?.id
        if (!userId) {
          commit('SET_ERROR', '请先登录')
          return false
        }
        
        const sceneWithUser = {
          ...scene,
          userId, // 添加用户ID
          id: Date.now().toString(),
          createdAt: new Date().toISOString()
        };
        
        const response = await api.createScene(sceneWithUser);
        commit('ADD_SCENE', response.data);
        return true;
      } catch (error) {
        commit('SET_ERROR', '创建场景失败');
        console.error(error);
        return false;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    //删除场景
    async deleteScene({ commit }, sceneId) {
      try {
        // 如果使用 json-server
        await api.delScene(sceneId)
        // 更新前端状态
        console.log(sceneId)
        commit('REMOVE_SCENE', sceneId);
        return true;
      } catch (error) {
        console.error('删除场景失败:', error);
        return false;
      }
    },

    // 更新场景设备列表
    async updateSceneDevices({ commit }, { sceneId, devices }) {
      try {
        console.log('更新场景设备列表...');
        console.log(sceneId);
        console.log(devices);
        await api.updateSceneDevices(sceneId, devices);
        commit('UPDATE_SCENE_DEVICES', { sceneId, devices });
      } catch (error) {
        commit('SET_ERROR', error.message);
      }
    },

  },



  getters: {
    getDevicesByRoom: (state) => {
      if (state.selectedRoom === 'all') {
        return state.devices
      }
      return state.devices.filter(
        (device) => device.roomId === state.selectedRoom
      )
    },
    getDeviceById: (state) => (id) => {
      return state.devices.find((device) => device.id === id)
    },
    isAuthenticated: state => !!state.user,
    currentUser: state => state.user,
    getRegisterError: state => state.error,
    isLoading: state => state.loading
  }

})