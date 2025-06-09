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
    user: null
  },
  mutations: {
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

    async toggleDevice({ commit }, { id, status }) {
      try {
        const response = await api.updateDevice(id, { status })
        commit('UPDATE_DEVICE', response.data)
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
    async login({ commit, dispatch }, credentials) {
      try {
        const response = await api.getUsers({
          name: credentials.username,
          password: credentials.password
        })
        
        if (response.data.length > 0) {
          commit('SET_USER', response.data[0]);
          
          // 登录成功后立即获取该用户的数据
          await Promise.all([
            dispatch('fetchDevices'),
            dispatch('fetchRooms'), 
            dispatch('fetchScenes')
          ]);
          
          return true
        }
        return false
      } catch (error) {
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

    async register({ commit, dispatch }, userData) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        console.log('开始注册...', userData);
        
        const existingUsers = await api.getUsers({ name: userData.username });
        console.log('现有用户查询结果:', existingUsers);
        
        if (existingUsers.data.length > 0) {
          commit('SET_ERROR', '用户名已存在');
          return false;
        }
        
        const newUser = {
          id: Date.now().toString(),
          name: userData.username,
          password: userData.password,
          role: 'member',
          permissions: ['read', 'write']
        };
        
        if (userData.email) {
          newUser.email = userData.email;
        }
        
        console.log('准备创建用户:', newUser);
        
        const response = await api.createUser(newUser);
        console.log('创建用户成功:', response.data);
        
        commit('SET_USER', response.data);
        
        // 注册成功后获取数据
        await Promise.all([
          dispatch('fetchDevices'),
          dispatch('fetchRooms'), 
          dispatch('fetchScenes')
        ]);
        
        return true;
      } catch (error) {
        console.error('注册失败详情:', error);
        commit('SET_ERROR', '注册失败，请重试');
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

    // 激活场景
    activateScene({ state, commit, dispatch }, sceneId) {
      return new Promise((resolve) => {
        setTimeout(() => {
          const scene = state.scenes.find(s => s.id === sceneId)
          if (scene) {
            alert(`场景 "${scene.name}" 已激活！`)
          }
          resolve()
        }, 500)
      })
    }
  },

  getters: {
    getDevicesByRoom: (state) => {
      if (state.selectedRoom === 'all') {
        return state.devices
      }
      return state.devices.filter(
        (device) => device.room === state.selectedRoom
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