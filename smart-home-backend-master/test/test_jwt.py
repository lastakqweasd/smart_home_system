import unittest
import requests
import json
from datetime import datetime, timedelta
import jwt
import random

BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "username": f"testuser_{random.randint(1, 100000)}",
    "email": f"test_{random.randint(1, 100000)}@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "phone": "138" + str(random.randint(10000000, 99999999)),
    "nickname": f"测试用户_{random.randint(1, 100000)}"
}

class TestJWTAuthentication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 注册测试用户
        register_url = f"{BASE_URL}/auth/register/"
        response = requests.post(register_url, json=TEST_USER)
        if response.status_code != 201:
            print("测试用户可能已存在，尝试继续测试")

    @classmethod
    def tearDownClass(cls):
        # 清理：删除测试用户（需要管理员权限实现）
        pass

    def setUp(self):
        # 每个测试前获取新令牌
        login_url = f"{BASE_URL}/auth/login/"
        self.login_response = requests.post(login_url, json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        })
        self.access_token = self.login_response.json().get('tokens', {}).get('access')
        self.refresh_token = self.login_response.json().get('tokens', {}).get("refresh")
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def test_1_successful_login(self):
        """测试成功登录"""
        self.assertEqual(self.login_response.status_code, 200)
        self.assertIn("access", self.login_response.json())
        self.assertIn("refresh", self.login_response.json())

    def test_2_invalid_login(self):
        """测试无效凭证登录"""
        response = requests.post(f"{BASE_URL}/auth/login/", json={
            "username": TEST_USER["username"],
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401)

    def test_3_access_protected_endpoint(self):
        """测试使用有效令牌访问受保护端点"""
        response = requests.get(f"{BASE_URL}/auth/profile/", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], TEST_USER["username"])

    def test_4_access_without_token(self):
        """测试无令牌访问受保护端点"""
        response = requests.get(f"{BASE_URL}/auth/profile/")
        self.assertEqual(response.status_code, 401)

    def test_5_access_with_invalid_token(self):
        """测试无效令牌访问"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_6_token_refresh(self):
        """测试令牌刷新"""
        refresh_url = f"{BASE_URL}/auth/token/refresh/"
        response = requests.post(refresh_url, json={"refresh": self.refresh_token})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())

        # 使用新令牌访问
        new_access = response.json()["access"]
        headers = {"Authorization": f"Bearer {new_access}"}
        profile_response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
        self.assertEqual(profile_response.status_code, 200)

    def test_7_reuse_refresh_token(self):
        """测试刷新令牌不能重复使用"""
        refresh_url = f"{BASE_URL}/auth/token/refresh/"
        
        # 第一次使用刷新令牌
        response1 = requests.post(refresh_url, json={"refresh": self.refresh_token})
        self.assertEqual(response1.status_code, 200)
        
        # 尝试再次使用相同的刷新令牌
        response2 = requests.post(refresh_url, json={"refresh": self.refresh_token})
        self.assertEqual(response2.status_code, 401)

    def test_8_logout_invalidates_token(self):
        """测试注销使令牌失效"""
        logout_url = f"{BASE_URL}/auth/logout/"
        logout_response = requests.post(logout_url, headers=self.headers)
        self.assertEqual(logout_response.status_code, 200)
        
        # 尝试使用已注销的令牌
        profile_response = requests.get(f"{BASE_URL}/auth/profile/", headers=self.headers)
        self.assertEqual(profile_response.status_code, 401)

    def test_9_expired_token(self):
        """测试过期令牌"""
        # 使用当前有效的令牌但立即使其过期（模拟）
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        # 尝试访问需要认证的端点（通常令牌不会立即过期，这里可能需要模拟）
        # 更好的方式是测试API对明显过期令牌的响应
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.4Adcj3UFYzPUVaVF43FmMab6RlaQD8A9V8wFzzht-KQ"  # 明显过期的示例令牌
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_A_change_password_flow(self):
        """测试修改密码流程"""
        # 修改密码
        change_pwd_url = f"{BASE_URL}/auth/change-password/"
        new_password = "NewPass123!"
        response = requests.post(change_pwd_url, headers=self.headers, json={
            "old_password": TEST_USER["password"],
            "new_password": new_password
        })
        self.assertEqual(response.status_code, 200)
        
        # 用旧密码尝试登录
        old_login = requests.post(f"{BASE_URL}/auth/login/", json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        })
        self.assertEqual(old_login.status_code, 401)
        
        # 用新密码登录
        new_login = requests.post(f"{BASE_URL}/auth/login/", json={
            "username": TEST_USER["username"],
            "password": new_password
        })
        self.assertEqual(new_login.status_code, 200)
        
        # 恢复测试密码
        requests.post(change_pwd_url, headers=self.headers, json={
            "old_password": new_password,
            "new_password": TEST_USER["password"]
        })

if __name__ == "__main__":
    unittest.main()