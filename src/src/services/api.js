import axios from 'axios'

// const API_URL = 'http://localhost:3000'
const API_URL = 'http://localhost:8000/api'

export const api = {
  // // 用户相关API
   getUsers: (params) => axios.get(`${API_URL}/users`, { params }),
  // login: (username, password) => axios.post(`${API_URL}/login`,JSON.stringify({ username, password}),{headers: {
  //     'Content-Type': 'application/json',
  //     'X-Requested-With': 'XMLHttpRequest'
  //   }}),
  // createUser: (userData) => axios.post(`${API_URL}/users`, userData),  
  login: async (param) => {
    // 登录
    return await fetch(`${API_URL}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: param['name'],
            // username: "admin",
            password: param['password']
            // password: "admin123"
          },
        )
    });
  },
  createUser: (userData) => axios.post(`${API_URL}/auth/register/`, {
    username: userData.username,
    password: userData.password,
    password_confirm: userData.password_confirm, // 注意字段名转换
    // 可选字段处理
    email: userData.email || null,  // 显式设置为null而不是空字符串
    phone: userData.phone || null,
    nickname: userData.nickname || userData.username // 默认用用户名作为昵称
  }, {
    headers: {
      'Content-Type': 'application/json'
    }
  }),
  postUser: (userData) => axios.post(`${API_URL}/users`, userData),    
  // 设备相关API
  getAllDevices: (access_token) => {
    return axios.get(`${API_URL}/devices`,{
      headers: {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json'
      }
    }
    );
  },
  ///////////
  getDevice: (id) => axios.get(`${API_URL}/devices/${id}`),
  updateDevice: (id, data, access_token) => {
    return axios.patch(`${API_URL}/devices/${id}/`, 
        data,
      {
        headers: {
          'Authorization': `Bearer ${access_token}`,
          'Content-Type': 'application/json'
        }
      }
    )
  },
  postDevice:(device, extra, access_token) => axios.post(`${API_URL}/devices/`, 
    {
      name: device.name,
      brand: device.brand,
      type: device.type,
      room: device.roomId,
      status: device.status,
      extra: extra,
      owner: device.userId,
      ip: '192.168.1.1',
      port: 8080,
    },
    {
      headers: {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json'
      }
    }
  ),
  delDevice:(deviceId, access_token) => axios.delete(`${API_URL}/devices/${deviceId}/`,
    {
      headers: {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json'
      }
    }
  ),

  // 房间相关API
  getRooms: (access_token) => axios.get(`${API_URL}/rooms/`, 
    {
      headers: {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json'
      }  
    }
  ),

  // 房间管理 API
  createRoom: (room,access_token) => {
    console.log('createRoom')
    console.log(room);
    console.log(room.name);
    console.log(room.id);
    console.log(access_token);
    console.log(typeof room.id);
    return axios.post(`${API_URL}/rooms/`, 
    {
      id: room.id,
      // id:1231232,
      name: room.name,
    },
    {
      headers: {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json'
      }
    }
  )
  },
  delRoom: (roomId) => axios.delete(`${API_URL}/rooms/${roomId}`),
  updateRoom: (roomId, data) => axios.patch(`${API_URL}/rooms/${roomId}`, data),

  // 场景相关API
  getScenes: (access_token) => axios.get(`${API_URL}/scenes/`,
    {
      headers: {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json'
      }
    }
  ),
  createScene: (sceneData, access_token) => axios.post(`${API_URL}/scenes/`, 
    sceneData,
    {
      headers: {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json'
      }
    },
  ),
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
  delScene: (sceneId, access_token) => axios.delete(`${API_URL}/scenes/${sceneId}/`,
    {
      headers: {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json'
      }
    }
  ),

  // 更新场景中的设备状态（部分更新）
  updateSceneDevices: (sceneId, deviceUpdates, access_token) => {
    // deviceUpdates 应该是一个对象数组，每个对象包含设备ID和要更新的字段
    return axios.patch(`${API_URL}/scenes/${sceneId}/`, 
      {devices:deviceUpdates}, 
      {
        headers: {
          'Authorization': `Bearer ${access_token}`,
          'Content-Type': 'application/json'
        }
      }
    );
  },
}