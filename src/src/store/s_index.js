import { createStore, Store } from 'vuex'
import { api } from '@/services/api'
import { userSetter } from 'core-js/stable/symbol';

export default createStore({
  state: {
    devices: [],
    rooms: [],
    scenes: [],
    selectedRoom: 'all',
    loading: false,
    error: null,
    user: null,
    tokens: null,
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
    SET_USER(state, payload) {
      state.user = payload.user
      console.log('获取令牌', payload.tokens)
      state.tokens = payload.tokens
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
        await api.delDevice(deviceId, state.tokens.access)
        commit('REMOVE_DEVICE', deviceId);
        return true;
      } catch (error) {
        console.error('删除设备失败:', error);
        return false;
      }
    },

    // 添加设备 - 关联当前用户
    async addDevice({ commit, state }, device) {
      console.log('添加设备：', device);
      commit('SET_LOADING', true);
      try {
        const userId = state.user?.id
        if (!userId) {
          commit('SET_ERROR', '请先登录')
          return false
        }
        
        // 添加用户ID到设备数据
        const deviceWithUser = { ...device, userId }
        const access_token = state.tokens.access
        //设置extra字段
        // 设备配置映射表
        function createExtra(device) {
          switch(device.type) {
            case 'light':
              return { brightness: device.brightness, color: '#FFDD88' };
            case 'ac':
              return { temperature:  device.temperature};
            case 'curtain':
              return { openPercentage: device.openPercentage};
            default:
              return {};
          }
        }

        // 使用extra
        const extra = createExtra(device); // { temperature: 25 }
        ////////////
        console.log(extra)
        console.log('添加用户ID到设备数据：', deviceWithUser);
        const response = await api.postDevice(deviceWithUser, extra, access_token)
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
        const access_token = await state.tokens.access
        const response = await api.getAllDevices(access_token)
        // 设置当前用户设备
        commit('SET_DEVICES', response.data)
      } catch (error) {
        commit('SET_ERROR', '获取设备列表失败')
        console.error(error)
      } finally {
        commit('SET_LOADING', false)
      }
    },

    // 获取房间 - 保持所有用户共享
    async fetchRooms({ commit, state}) {
      try {
        const access_token = state.tokens.access;
        const response = await api.getRooms(access_token)
        console.log("获取房间成功：", response.data)
        commit('SET_ROOMS', response.data)
      } catch (error) {
        commit('SET_ERROR', '获取房间列表失败')
        console.error(error)
      }
    },

    // 获取场景 - 只获取当前用户的场景
    async fetchScenes({ commit, state }) {
      try {
        const access_token = state.tokens.access;
        const response = await api.getScenes(access_token)
        const data = await response.data;
        console.log("获取场景成功：", data)
        // 设置用户当前版本
        commit('SET_SCENES', data)
        console.log(state.devices)
        console.log(state.devices.length)
      } catch (error) {
        commit('SET_ERROR', '获取场景列表失败')
        console.error(error)
      }
    },

    setSelectedRoom({ commit }, room) {
      commit('SET_SELECTED_ROOM', room)
    },

    async createRoom({ commit , state}, roomData) {
      const access_token = state.tokens.access;
      commit('SET_LOADING', true);
      try {
        const newRoom = {
          id: Date.now().toString(),
          name: roomData.name,
        };
        console.log('新房间为：');
        console.log(newRoom);
        // 调用API创建房间
        console.log('调用API创建房间...');
        const response = await api.createRoom(newRoom, access_token);
        console.log('创建房间成功：', response.data);
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

    async toggleDevice({ commit, state }, { id, status }) {
      try {
        console.log(id)
        console.log({status})
        if (status === undefined) {
          console.error(`toggleDevice: Invalid status for device ${id}`);
          return;
        }
        const response = await api.updateDevice(id, { status }, state.tokens.access)
        const updatedDevice = response.data
        commit('UPDATE_DEVICE', updatedDevice)
      } catch (error) {
        commit('SET_ERROR', '设备状态更新失败')
        console.error(error)
      }
    },

    async updateDevice({ commit, state }, { id, data }) {
      try {
        console.log('updateDevice')
        console.log(id)
        console.log(data)
        const response = await api.updateDevice(id, data, state.tokens.access)
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

    async login({ commit, dispatch }, credentials) {
      try {
        console.log('s_inde_开始登录...', credentials);
        const response = await api.login({
          name: credentials.username,
          password: credentials.password
        });
        const data = await response.json();
        console.log('获取data: ', data);
        if (data.success) {
          console.log('登录成功!');
          console.log(data.user);
          console.log(data.tokens);
          commit('SET_USER', {user: data.user, tokens: data.tokens});
          console.log('查看状态：', this.state);
          console.log('set user ok !');
          // 登录成功后立即获取该用户的数据
          await Promise.all([
            dispatch('fetchDevices'),
            dispatch('fetchRooms'), 
            dispatch('fetchScenes')
          ]);
          console.log("qwewqe");
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
      console.log("assdq")
      try {
        console.log('创建场景：', scene);
        const userId = state.user?.id
        if (!userId) {
          commit('SET_ERROR', '请先登录')
          return false
        }
        
        // const sceneWithUser = {
        //   ...scene,
        //   userId, // 添加用户ID
        //   id: Date.now().toString(),
        //   createdAt: new Date().toISOString()
        // };
        const test = {
          "name": "回家模式",
          "description": "一键打开客厅灯和空调",
          "device_configs": [
          ]
        }
        console.log(test)
        const scenedata = scene
        console.log(scenedata)
        const response = await api.createScene(scenedata, state.tokens.access);
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
    async deleteScene({ commit , state}, sceneId) {
      try {
        // 如果使用 json-server
        await api.delScene(sceneId, state.tokens.access)
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