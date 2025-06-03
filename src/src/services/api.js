import axios from 'axios'

const API_URL = 'http://localhost:3000'

export const api = {
  // 用户相关API
  getUsers: (params) => axios.get(`${API_URL}/users`, { params }),

  // 设备相关API
  getAllDevices: () => axios.get(`${API_URL}/devices`),
  getDevice: (id) => axios.get(`${API_URL}/devices/${id}`),
  updateDevice: (id, data) => axios.patch(`${API_URL}/devices/${id}`, data),
  postDevice:(device) => axios.post(`${API_URL}/devices`, device),
  delDevice:(deviceId) => axios.delete(`${API_URL}/devices/${deviceId}`),

  // 房间相关API
  getRooms: () => axios.get(`${API_URL}/rooms`),

  // 场景相关API
  getScenes: () => axios.get(`${API_URL}/scenes`),
  createScene: (sceneData) => axios.post(API_URL+'/scenes', sceneData),
  activateScene: async (sceneId) => {
    const res = await axios.get(`${API_URL}/scenes/${sceneId}`);
    const scene = res.data;
    const allDevices = (await axios.get(`${API_URL}/devices`)).data;
    
    const updatePromises = scene.devices.flatMap(targetDevice => {
      // 查找匹配的设备
      const matchedDevices = allDevices.filter(device => 
        device.type === targetDevice.type && 
        device.room === targetDevice.room
      );
      
      // 为每个匹配设备创建更新请求
      return matchedDevices.map(device => 
        axios.patch(`${API_URL}/devices/${device.id}`, targetDevice)
      );
    });

    await Promise.all(updatePromises);
    return scene;
  }
}