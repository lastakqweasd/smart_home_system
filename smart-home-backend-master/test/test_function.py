'''
测试用例1:功能测试
'''
import requests
import json
import sys

base_url="http://localhost:8000/api"    #后端运行的API地址
#新创建的一个用户
data1 = {        #这里每一次运行之后有更新，需要重新设定邮箱和名字，当然，如果重置了数据库就不用
    "username": "newname",
    "email": "newemail@qq.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "phone": "13800138000",
    "nickname": "测试用户djt123"
}

# 1. 测试用户认证的功能是否正常运行
def testRegister():
    print("=== 测试用户注册 ===")
    url = f"{base_url}/auth/register/"
    data2 = {       #部分字段为空，模拟的是前端用户忘记填写某个字段
        "username": "user3",
        "email": "",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "phone": "13728973026",
        "nickname": "测试用户3"
    }   
    data3 = {       #密码不同，模拟的是前端输入两次密码不正确的情况
        "username": "user4",
        "email": "user4mail@qq.com",
        "password": "testpass123",
        "password_confirm": "123test",
        "phone": "13728973026",
        "nickname": "测试用户4"
    }
    data4 = {       #邮箱重复的情况
        "username": "user102830",
        "email": "djt@mail2.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "phone": "13800138000",
        "nickname": "测试用户djt123"
    }
    data5 = {       #手机号码不是11位的情况
        "username": "user129837",
        "email": "djt3@mail2.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "phone": "13838000",
        "nickname": "测试用户djt123"
    }
    data6 = {
        "username": data1["username"],
        "email": "djt3@mail2.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "phone": "13838000",
        "nickname": "测试用户djt123"
    }
    test_data = [data1,data2,data3,data4,data5,data6]
    test_descriptions = [
        "测试正常注册",
        "测试用户忘记填写某个字段",
        "测试两次输入密码不同的情况",
        "测试邮箱重复的情况",
        "测试手机号码错误的情况",
        "测试用户名重复的情况"
    ]
    flag=None
    for i, (data, description) in enumerate(zip(test_data, test_descriptions), start=1):
        print(f"测试 {i}: {description}")
        try:
            response = requests.post(url, json=data)
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            if response.status_code == 201: #创建成功
                print("注册成功！")
                #print(f"注册内容: {response.json()}")       #如果创建失败那么就是空，没有格式
                if (i==1) :
                    flag=response.json().get('tokens', {}).get('access')
            else:
                print("注册失败")
        except Exception as e:  #这里出现异常的情况正常情况下是请求超时或者是我的编码失误
            print(f"请求失败: {e}")
    return flag

#2. 测试用户登录
def test_login():
    print("=== 测试用户登录 ===")
    url = f"{base_url}/auth/login/"
    data2 = {
        "username": data1["username"],
        "password": data1["password"]
    }
    data3 = {
        "username": data1["username"],
        "password": ""
    }
    data4= {
        "username": "",
        "password": data1["password"]
    }
    data5={
        "username": data1["username"],
        "password": "!!!"
    }
    data6={
        "username": "NotThisUser",
        "password": "1234123"
    }
    test_data = [data2,data3,data4,data5,data6]
    test_descriptions = [
        "测试正常登录",
        "测试无密码",
        "测试无用户名",
        "测试密码错误",
        "测试用户名不存在"
    ]
    flag=None
    for i, (data, description) in enumerate(zip(test_data, test_descriptions), start=1):
        print(f"测试 {i}: {description}")
        try:
            response = requests.post(url, json=data)
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            if response.status_code == 200:
                flag={
                    "access_token":response.json().get('tokens', {}).get('access'),
                    "refresh_token":response.json().get('tokens', {}).get('refresh')
                }
            else:
                print("登录失败")
        except Exception as e:  
            print(f"请求失败: {e}")
    return flag

#3. 测试用户注销
def test_logout(token):
    print("=== 测试用户注销 ===")
    url = f"{base_url}/auth/logout/"
    headers = {
        "Authorization": f"Bearer {token['access_token']}"  # 使用 access_token 进行认证
    }
    data2 = {
        "refresh_token": token["refresh_token"]
    }
    response = requests.post(url, json=data2, headers=headers)
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

#4. 测试用户信息管理
def test_information(token):
    user_infor=None
    print("=== 测试用户资料管理 ===")
    #测试获取用户信息
    headers = {
        "Authorization": f"Bearer {token['access_token']}"  # 使用 access_token 进行认证
    }
    print(f"测试 1: 测试获取用户信息")
    try:
        url = f"{base_url}/auth/profile/"
        response = requests.get(url, json=None, headers=headers)    #实际上只需要access_token就可以了
        user_infor=response.json()["user"]
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        if response.status_code==201:
            print("获取信息成功")
        else:
            print("获取信息失败")
    except Exception as e:  
        print(f"请求失败: {e}")
    '''   
    print(f"测试 2: 更新用户信息")
    data = {    #规定好的格式
        "email": user_infor["email"],  #可以更新邮箱
        "phone": user_infor["phone"],            #可以更新手机号
        "nickname": user_infor["nickname"],             #可以更新昵称
        "bio": user_infor["bio"],              # 更新简介
        "first_name": user_infor["first_name"],                # 更新名字
        "last_name": user_infor["last_name"],                 # 更新姓氏
    }
    try:
        url = f"{base_url}/auth/profile/"
        response = requests.put(url, json=data, headers=headers)    #实际上只需要access_token就可以了
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        if response.status_code==201 :
            print("修改信息成功")
        else :
            print("修改信息失败")
    except Exception as e:  
        print(f"请求失败: {e}")
    '''
    
    print(f"测试 3: 用户密码修改测试")
    url = f"{base_url}/auth/change-password/"
    data2={
        "old_password": data1["password"],
        "new_password": "djt1231478",
        "new_password_confirm": "djt1231478"
    }
    data3={
        "old_password": data1["password"],
        "new_password": "djt1234567",
        "new_password_confirm": "djt1234567"
    }
    data4={
        "old_password": data2["new_password"],
        "new_password": "djt12345678",
        "new_password_confirm": "djt1234567"
    }
    data5={
        "old_password": data2["new_password"],
        "new_password": "",
        "new_password_confirm": "djt1212334567"
    }
    data1["password"]=data1["password_confirm"]=data2["new_password"]   #更新全局的一个信息
    test_data = [data2,data3,data4,data5]
    test_descriptions = [
        "测试正常修改密码",
        "测试旧密码错误",
        "测试两次新密码不一样",
        "测试未填入密码"
    ]
    for i, (data, description) in enumerate(zip(test_data, test_descriptions), start=1):
        print(f"测试 3.{i}: {description}")
        try:
            response = requests.post(url, json=data, headers=headers)    #实际上只需要access_token就可以了
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            if response.status_code==201:
                print("修改密码成功")
            else :
                print("修改密码失败")
        except Exception as e:  
            print(f"请求失败: {e}")

#5. 测试房间
def test_room(token):
    # 测试数据
    test_room = {
        "name": "测试房间"
    }
    print("\n=== 测试房间管理 ===")
    
    headers = {
        "Authorization": f"Bearer {token['access_token']}"  # 使用 access_token 进行认证
    }
    url = f"{base_url}/api/rooms/"
    
    # 1. 创建房间
    print("\n1. 测试创建房间")
    response = requests.post(url, json=test_room, headers=headers)
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    room_id = response.json().get('id') if response.status_code == 201 else None
    
    # 2. 获取房间列表
    print("\n2. 测试获取房间列表")
    response = requests.get(url, headers=headers)
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 3. 更新房间
    if room_id:
        print("\n3. 测试更新房间")
        update_url = f"{url}{room_id}/"
        update_data = {"name": "更新后的房间名"}
        response = requests.put(update_url, json=update_data, headers=headers)
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 4. 删除房间
    if room_id:
        print("\n4. 测试删除房间")
        delete_url = f"{url}{room_id}/"
        response = requests.delete(delete_url, headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 204:
            print("删除成功")
    
    return room_id

#6. 测试设备管理
def test_device_management(token,room_id):
    test_device = {
        "name": "测试设备",
        "type": "light",
        "room": None,  # 将在测试中动态设置
        "status": False,
        "extra": {"brightness": 50, "color": "#FFFFFF"},
        "brand": "测试品牌"
    }
    print("\n=== 测试设备管理 ===")
    headers = {
        "Authorization": f"Bearer {token['access_token']}"  # 使用 access_token 进行认证
    }
    url = f"{base_url}/api/devices/"
    
    # 准备测试数据
    test_device_data = test_device.copy()
    test_device_data["room"] = room_id
    
    # 1. 创建设备
    print("\n1. 测试创建设备")
    response = requests.post(url, json=test_device_data, headers=headers)
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    device_id = response.json().get('id') if response.status_code == 201 else None
    
    # 2. 获取设备列表
    print("\n2. 测试获取设备列表")
    response = requests.get(url, headers=headers)
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 3. 获取设备详情
    if device_id:
        print("\n3. 测试获取设备详情")
        detail_url = f"{url}{device_id}/"
        response = requests.get(detail_url, headers=headers)
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 4. 更新设备
    if device_id:
        print("\n4. 测试更新设备")
        update_url = f"{url}{device_id}/"
        update_data = {
            "name": "更新后的设备名",
            "status": True,
            "extra": {"brightness": 75}
        }
        response = requests.put(update_url, json=update_data, headers=headers)
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 5. 删除设备
    if device_id:
        print("\n5. 测试删除设备")
        delete_url = f"{url}{device_id}/"
        response = requests.delete(delete_url, headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 204:
            print("删除成功")
    
    return device_id

#7. 测试场景管理功能
def test_scene_management(token,device_id):
    test_scene = {
        "name": "测试场景",
        "description": "这是一个测试场景",
        "device_configs": [
            {
                "device": None,  # 将在测试中动态设置
                "status": True,
                "config": {"brightness": 100}
            }
        ]
    }
    print("\n=== 测试场景管理 ===")
    headers = {
        "Authorization": f"Bearer {token['access_token']}"  # 使用 access_token 进行认证
    }
    url = f"{base_url}/api/scenes/"
    
    # 准备测试数据
    test_scene_data = test_scene.copy()
    test_scene_data["device_configs"][0]["device"] = device_id
    
    # 1. 创建场景
    print("\n1. 测试创建场景")
    response = requests.post(url, json=test_scene_data, headers=headers)
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    scene_id = response.json().get('id') if response.status_code == 201 else None
    
    # 2. 获取场景列表
    print("\n2. 测试获取场景列表")
    response = requests.get(url, headers=headers)
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 3. 更新场景
    if scene_id:
        print("\n3. 测试更新场景")
        update_url = f"{url}{scene_id}/"
        update_data = {
            "name": "更新后的场景名",
            "description": "更新后的描述",
            "device_configs": [
                {
                    "device": device_id,
                    "status": False,
                    "config": {"brightness": 50}
                }
            ]
        }
        response = requests.put(update_url, json=update_data, headers=headers)
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 4. 激活场景
    if scene_id:
        print("\n4. 测试激活场景")
        activate_url = f"{url}{scene_id}/activate/"
        response = requests.post(activate_url, headers=headers)
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 5. 删除场景
    if scene_id:
        print("\n5. 测试删除场景")
        delete_url = f"{url}{scene_id}/"
        response = requests.delete(delete_url, headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 204:
            print("删除成功")

# 8. 超级管理员测试
admin_auth_token = None  # 用于存储超级管理员认证token
member_auth_token = None  # 用于存储普通用户认证token

# 测试数据 - 管理员
admin_credentials = {
    "username": "admin",  # 替换为实际的超级管理员用户名
    "password": "admin123"  # 替换为实际的超级管理员密码
}

# 测试数据 - 普通用户
test_member_user = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "test123",
    "role": "member",
    "phone": "13800138000",
    "nickname": "测试用户",
    "is_active": True
}

test_admin_user = {
    "username": "testadmin",
    "email": "testadmin@example.com",
    "password": "test123",
    "role": "admin",
    "phone": "13800138001",
    "nickname": "测试管理员",
    "is_active": True
}


#超级管理员登录
def test_admin_login():
    print("\n=== 测试超级管理员登录 ===")
    url = f"{base_url}/auth/login/"
    # 测试数据 - 管理员
    admin_credentials = {
        "username": "admin",  # 替换为实际的超级管理员用户名
        "password": "admin123"  # 替换为实际的超级管理员密码
    }
    try:
        response = requests.post(url, json=admin_credentials)
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        if response.status_code == 200:
            return {
                "access_token": response.json().get('tokens', {}).get('access'),
                "refresh_token": response.json().get('tokens', {}).get('refresh')
            }
        else:
            print("管理员登录失败")
            return None
    except Exception as e:
        print(f"请求失败: {e}")
        return None
    
def test_admin_user_management():
    """测试超级管理员对用户的管理功能"""
    print("\n=== 测试超级管理员用户管理 ===")
    global admin_auth_token, member_auth_token
    
    if not admin_auth_token:
        print("需要先登录超级管理员")
        return
    
    headers = {"Authorization": f"Bearer {admin_auth_token['access_token']}"}
    url = f"{base_url}/api/users/"
    
    # 1. 创建普通用户
    print("\n1. 测试创建普通用户")
    response = requests.post(url, json=test_member_user, headers=headers)
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    member_user_id = response.json().get('id') if response.status_code == 201 else None
    
    # 2. 创建管理员用户
    print("\n2. 测试创建管理员用户")
    response = requests.post(url, json=test_admin_user, headers=headers)
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    admin_user_id = response.json().get('id') if response.status_code == 201 else None
    
    # 3. 获取用户列表
    print("\n3. 测试获取用户列表")
    response = requests.get(url, headers=headers)
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 4. 按角色筛选用户
    print("\n4. 测试按角色筛选用户")
    filter_url = f"{url}?role=member"
    response = requests.get(filter_url, headers=headers)
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 5. 获取用户详情
    if member_user_id:
        print("\n5. 测试获取用户详情")
        detail_url = f"{url}{member_user_id}/"
        response = requests.get(detail_url, headers=headers)
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 6. 更新用户信息
    if member_user_id:
        print("\n6. 测试更新用户信息")
        update_url = f"{url}{member_user_id}/"
        update_data = {
            "nickname": "更新后的昵称",
            "phone": "13900139000",
            "bio": "这是更新后的个人简介"
        }
        response = requests.put(update_url, json=update_data, headers=headers)
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 7. 禁用用户
    if member_user_id:
        print("\n7. 测试禁用用户")
        deactivate_url = f"{url}{member_user_id}/deactivate/"
        response = requests.post(deactivate_url, headers=headers)
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # 测试被禁用用户登录
        member_auth_token = test_login(test_member_user["username"], test_member_user["password"])  #用户登录
    
    # 8. 激活用户
    if member_user_id:
        print("\n8. 测试激活用户")
        activate_url = f"{url}{member_user_id}/activate/"
        response = requests.post(activate_url, headers=headers)
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # 测试激活后用户登录
        member_auth_token = test_login(test_member_user["username"], test_member_user["password"])  #用户登录
    
    # 9. 删除用户
    if member_user_id:
        print("\n9. 测试删除用户")
        delete_url = f"{url}{member_user_id}/"
        response = requests.delete(delete_url, headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 204:
            print("用户删除成功")
    
    if admin_user_id:
        print("\n10. 测试删除管理员用户")
        delete_url = f"{url}{admin_user_id}/"
        response = requests.delete(delete_url, headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 204:
            print("管理员用户删除成功")

def test_member_user_access():
    """测试普通用户对用户管理API的访问权限"""
    print("\n=== 测试普通用户权限 ===")
    global member_auth_token
    
    if not member_auth_token:
        print("需要先创建并登录普通用户")
        return
    
    headers = {"Authorization": f"Bearer {member_auth_token['access_token']}"}
    url = f"{base_url}/api/users/"
    
    # 1. 尝试获取用户列表 (应该被拒绝)
    print("\n1. 测试普通用户尝试获取用户列表")
    response = requests.get(url, headers=headers)
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 2. 尝试创建用户 (应该被拒绝)
    print("\n2. 测试普通用户尝试创建用户")
    response = requests.post(url, json=test_member_user, headers=headers)
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    access_token=testRegister()    #获取新用户的token
    token=test_login()              #通过登录入口获取用户的token
    #test_logout(token)             #用户注销测试
    test_information(token)