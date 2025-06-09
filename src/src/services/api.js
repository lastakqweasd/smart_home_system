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
  updateDevice: (id, data) => axios.patch(`${API_URL}/devices/${id}`, data),
  postDevice:(device) => axios.post(`${API_URL}/devices`, device),
  delDevice:(deviceId) => axios.delete(`${API_URL}/devices/${deviceId}`),

  // 房间相关API
  getRooms: () => axios.get(`${API_URL}/rooms/`),

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
        device.room === targetDevice.room
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

  // activateScene: async (sceneId) => {
  //   try {
  //     // 1. 获取场景配置和所有设备
  //     const [sceneRes, devicesRes] = await Promise.all([
  //       axios.get(`${API_URL}/scenes/${sceneId}`),
  //       axios.get(`${API_URL}/devices`)
  //     ]);
  //     const scene = sceneRes.data;
  //     const allDevices = devicesRes.data;

  //     // 2. 找出场景中需要激活的设备ID集合
  //     const sceneDeviceIds = new Set();
  //     scene.devices.forEach(targetDevice => {
  //       allDevices.filter(device => 
  //         device.type === targetDevice.type && 
  //         device.room === targetDevice.room
  //       ).forEach(device => {
  //         sceneDeviceIds.add(device.id);
  //       });
  //     });

  //     // 3. 创建两类请求：
  //     //    - 激活场景中的设备
  //     //    - 关闭不在场景中的设备
  //     const updatePromises = [
  //       // 3.1 更新场景中的设备
  //       ...scene.devices.flatMap(targetDevice => {
  //         const matchedDevices = allDevices.filter(device => 
  //           device.type === targetDevice.type && 
  //           device.room === targetDevice.room
  //         );
  //         return matchedDevices.map(device => 
  //           axios.patch(`${API_URL}/devices/${device.id}/`, targetDevice)
  //         );
  //       }),
        
  //       // 3.2 关闭不在场景中的设备
  //       ...allDevices
  //         .filter(device => !sceneDeviceIds.has(device.id))
  //         .map(device => 
  //           axios.patch(`${API_URL}/devices/${device.id}/`, { power: false })
  //         )
  //     ];

  //     // 4. 批量执行所有更新
  //     await Promise.all(updatePromises);
  //     return scene;
      
  //   } catch (error) {
  //     console.error('场景激活失败:', error);
  //     throw new Error(`场景激活失败: ${error.message}`);
  //   }
  // },

}