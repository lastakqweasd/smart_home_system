import axios from 'axios'

const API_URL = 'http://localhost:3000'

export const api = {
  // // 用户相关API
   getUsers: (params) => axios.get(`${API_URL}/users`, { params }),
  // login: (username, password) => axios.post(`${API_URL}/login`,JSON.stringify({ username, password}),{headers: {
  //     'Content-Type': 'application/json',
  //     'X-Requested-With': 'XMLHttpRequest'
  //   }}),
  createUser: (userData) => axios.post(`${API_URL}/users`, userData),  
  postUser: (userData) => axios.post(`${API_URL}/users`, userData),    
  // 设备相关API
  getAllDevices: () => axios.get(`${API_URL}/devices`),
  getDevice: (id) => axios.get(`${API_URL}/devices/${id}`),
  updateDevice: (id, data) => {
    console.log(id, data);
    return axios.patch(`${API_URL}/devices/${id}`, data)
  },
  postDevice:(device) => axios.post(`${API_URL}/devices`, device),
  delDevice:(deviceId) => axios.delete(`${API_URL}/devices/${deviceId}`),

  // 房间相关API
  getRooms: () => axios.get(`${API_URL}/rooms/`),

  // 房间管理 API
  createRoom: (room) => axios.post(`${API_URL}/rooms`, room),
  delRoom: (roomId) => axios.delete(`${API_URL}/rooms/${roomId}`),
  updateRoom: (roomId, data) => axios.patch(`${API_URL}/rooms/${roomId}`, data),

  // 场景相关API
  getScenes: () => axios.get(`${API_URL}/scenes/`),
  createScene: (sceneData) => axios.post(API_URL+'/scenes', sceneData),
  activateScene: async (sceneId) => {
    const res = await axios.get(`${API_URL}/scenes/${sceneId}`);
    console.log(res);
    console.log(res.data);
    const scene = res.data;
    const allDevices = (await axios.get(`${API_URL}/devices`)).data;
    
    console.log(allDevices);
    const updatePromises = scene.devices.flatMap(targetDevice => {
      // 查找匹配的设备
      console.log(targetDevice);
      const matchedDevices = allDevices.filter(device => 
        device.type === targetDevice.type && 
        device.roomId === targetDevice.roomId
      );
      
      // 为每个匹配设备创建更新请求
      console.log(matchedDevices);
      return matchedDevices.map(device => 
        axios.patch(`${API_URL}/devices/${device.id}/`, targetDevice)
      );
    });
    console.log(updatePromises);
    await Promise.all(updatePromises);
    console.log(updatePromises);
    return scene;
  },

  //删除场景
  delScene: (sceneId) => axios.delete(`${API_URL}/scenes/${sceneId}`),

  // 更新场景中的设备状态（部分更新）
  updateSceneDevices: (sceneId, deviceUpdates) => {
    // deviceUpdates 应该是一个对象数组，每个对象包含设备ID和要更新的字段
    return axios.patch(`${API_URL}/scenes/${sceneId}/`, {devices:deviceUpdates});
  },
}