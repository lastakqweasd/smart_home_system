#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能家居系统 API 测试脚本
用于测试用户注册、登录和API访问功能
"""

import requests
import json
import sys

# API基础URL
BASE_URL = "http://localhost:8000/api"

def test_register():
    """测试用户注册"""
    print("=== 测试用户注册 ===")
    
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "phone": "13800138000",
        "nickname": "测试用户"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 201:
            return response.json().get('tokens', {}).get('access')
        else:
            print("注册失败")
            return None
    except Exception as e:
        print(f"注册请求失败: {e}")
        return None

def test_login():
    """测试用户登录"""
    print("\n=== 测试用户登录 ===")
    
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            return response.json().get('tokens', {}).get('access')
        else:
            print("登录失败")
            return None
    except Exception as e:
        print(f"登录请求失败: {e}")
        return None

def test_get_profile(access_token):
    """测试获取用户资料"""
    print("\n=== 测试获取用户资料 ===")
    
    url = f"{BASE_URL}/auth/profile/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"获取资料请求失败: {e}")

def test_get_devices(access_token):
    """测试获取设备列表"""
    print("\n=== 测试获取设备列表 ===")
    
    url = f"{BASE_URL}/devices/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"获取设备列表请求失败: {e}")

def test_create_device(access_token):
    """测试创建设备"""
    print("\n=== 测试创建设备 ===")
    
    url = f"{BASE_URL}/devices/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 首先获取房间列表
    rooms_url = f"{BASE_URL}/rooms/"
    rooms_response = requests.get(rooms_url, headers=headers)
    
    if rooms_response.status_code == 200:
        rooms = rooms_response.json()
        if rooms:
            room_id = rooms[0]['id']  # 使用第一个房间
        else:
            print("没有可用的房间，跳过设备创建测试")
            return
    else:
        print("获取房间列表失败，跳过设备创建测试")
        return
    
    data = {
        "name": "测试设备",
        "type": "light",
        "room": room_id,
        "status": True,
        "brand": "测试品牌",
        "extra": {"brightness": 80}
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"创建设备请求失败: {e}")

def test_unauthorized_access():
    """测试未授权访问"""
    print("\n=== 测试未授权访问 ===")
    
    url = f"{BASE_URL}/devices/"
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"未授权访问请求失败: {e}")

def main():
    """主测试函数"""
    print("智能家居系统 API 测试")
    print("=" * 50)
    
    # 测试未授权访问
    test_unauthorized_access()
    
    # 测试注册
    access_token = test_register()
    
    if not access_token:
        # 如果注册失败，尝试登录
        access_token = test_login()
    
    if access_token:
        # 测试需要认证的API
        test_get_profile(access_token)
        test_get_devices(access_token)
        test_create_device(access_token)
    else:
        print("无法获取访问令牌，测试终止")
        sys.exit(1)
    
    print("\n测试完成！")

if __name__ == "__main__":
    main() 