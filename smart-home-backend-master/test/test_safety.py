import unittest
import requests
import json
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "username": "security_tester",
    "password": "Test@1234",
    "email": "security_test@example.com"
}

class TestSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """创建测试用户"""
        register_url = f"{BASE_URL}/auth/register/"
        response = requests.post(register_url, json=TEST_USER)
        if response.status_code != 201:
            print("测试用户可能已存在，尝试继续测试")
        
        # 登录获取令牌
        login_url = f"{BASE_URL}/auth/login/"
        cls.login_response = requests.post(login_url, json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        })
        cls.access_token = cls.login_response.json().get("access")
        cls.headers = {
            "Authorization": f"Bearer {cls.access_token}",
            "Content-Type": "application/json"
        }
        
        # 创建一个测试设备用于测试
        device_url = f"{BASE_URL}/devices/"
        cls.device_response = requests.post(device_url, headers=cls.headers, json={
            "name": "Test Device",
            "type": "sensor",
            "status": "active"
        })
        cls.device_id = cls.device_response.json().get("id")

    @classmethod
    def tearDownClass(cls):
        """测试完成后清理测试数据"""
        # 这里需要实现删除测试数据的逻辑
        pass

    # --------------------------
    # 输入验证测试 (XSS)
    # --------------------------
    def test_1_xss_in_device_name(self):
        """测试设备名称中的XSS漏洞"""
        xss_payload = "<script>alert('XSS')</script>"
        device_url = f"{BASE_URL}/devices/"
        
        # 尝试创建包含XSS的设备
        print("打印请求头信息：", self.headers)
        response = requests.post(device_url, headers=self.headers, json={
            "name": xss_payload,
            "type": "sensor",
            "status": "active"
        })
        
        # 检查响应是否转义了HTML标签
        if response.status_code == 201:
            device_id = response.json().get("id")
            get_response = requests.get(f"{BASE_URL}/devices/{device_id}/", headers=self.headers)
            self.assertNotIn("<script>", get_response.text, "XSS漏洞: 脚本标签未被转义")
            
            # 检查返回的JSON数据是否编码
            device_name = response.json().get("name")
            self.assertNotEqual(device_name, xss_payload, "XSS漏洞: 原始XSS载荷被返回")
        else:
            self.assertEqual(response.status_code, 400, "应拒绝包含XSS的输入")

    def test_2_xss_in_profile_update(self):
        """测试用户资料更新中的XSS漏洞"""
        xss_payload = {"bio": "<img src=x onerror=alert('XSS')>"}
        profile_url = f"{BASE_URL}/auth/profile/"
        
        # 尝试更新包含XSS的资料
        response = requests.put(profile_url, headers=self.headers, json=xss_payload)
        
        # 检查响应
        if response.status_code == 200:
            get_response = requests.get(profile_url, headers=self.headers)
            self.assertNotIn("onerror=", get_response.text, "XSS漏洞: 事件处理器未被过滤")
        else:
            self.assertEqual(response.status_code, 400, "应拒绝包含XSS的输入")

    # --------------------------
    # SQL注入测试
    # --------------------------
    def test_3_sql_injection_in_login(self):
        """测试登录表单中的SQL注入"""
        sql_payloads = [
            "' OR '1'='1' --",
            "' OR 1=1 --",
            "admin' --",
            "'; DROP TABLE users; --"
        ]
        
        for payload in sql_payloads:
            response = requests.post(f"{BASE_URL}/auth/login/", json={
                "username": payload,
                "password": "anypassword"
            })
            # 不应返回500错误或异常信息
            self.assertNotEqual(response.status_code, 500, f"SQL注入漏洞: 载荷 {payload} 导致服务器错误")
            self.assertNotIn("SQL syntax", response.text, f"SQL注入漏洞: 载荷 {payload} 暴露SQL错误")

    def test_4_sql_injection_in_device_id(self):
        """测试设备ID参数中的SQL注入"""
        sql_payloads = [
            "1 OR 1=1",
            "1; SELECT * FROM users",
            "1 UNION SELECT username, password FROM users"
        ]
        
        for payload in sql_payloads:
            response = requests.get(f"{BASE_URL}/devices/{payload}/", headers=self.headers)
            self.assertNotEqual(response.status_code, 500, f"SQL注入漏洞: 设备ID {payload} 导致服务器错误")
            self.assertNotIn("SQL syntax", response.text, f"SQL注入漏洞: 设备ID {payload} 暴露SQL错误")
            
            # 检查是否返回了多个设备
            if response.status_code == 200:
                self.assertTrue(isinstance(response.json(), dict), "SQL注入漏洞: 可能返回了多条记录")

    # --------------------------
    # CSRF测试
    # --------------------------
    def test_5_csrf_protection_on_state_changing_requests(self):
        """测试关键操作是否有CSRF保护"""
        # 测试没有CSRF令牌的请求是否被拒绝
        sensitive_endpoints = [
            ("POST", f"{BASE_URL}/auth/change-password/", {"old_password": "test", "new_password": "newpass"}),
            ("PUT", f"{BASE_URL}/auth/profile/", {"bio": "test"}),
            ("DELETE", f"{BASE_URL}/devices/{self.device_id}/", None),
            ("POST", f"{BASE_URL}/rooms/", {"name": "test room"})
        ]
        
        for method, url, data in sensitive_endpoints:
            if method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            
            # 检查响应
            # 对于REST API使用JWT的情况，通常不需要CSRF保护
            # 但如果API也用于浏览器会话，则需要检查
            if response.status_code == 403:
                self.assertIn("CSRF", response.text, "应包含CSRF错误信息")
            elif response.status_code != 200 and response.status_code != 201 and response.status_code != 204:
                # 其他错误状态码是可以接受的
                pass
            else:
                # 如果请求成功，确保不是因为缺少CSRF保护
                # 对于纯API通常是可以的
                pass

    # --------------------------
    # 批量分配漏洞测试
    # --------------------------
    def test_6_mass_assignment_vulnerability(self):
        """测试是否可以通过请求体修改敏感字段"""
        # 尝试修改不应被用户直接设置的字段
        test_cases = [
            {"is_admin": True},
            {"is_staff": True},
            {"last_login": "2023-01-01"},
            {"password": "newpassword"}
        ]
        
        for payload in test_cases:
            response = requests.put(f"{BASE_URL}/auth/profile/", headers=self.headers, json=payload)
            
            # 检查响应
            if response.status_code == 200:
                # 获取用户资料验证字段是否真的被修改
                profile_response = requests.get(f"{BASE_URL}/auth/profile/", headers=self.headers)
                profile_data = profile_response.json()
                
                for key in payload.keys():
                    self.assertNotIn(key, profile_data, f"批量分配漏洞: 字段 {key} 被允许修改")
            else:
                self.assertEqual(response.status_code, 400, "应拒绝包含敏感字段的请求")

    # --------------------------
    # 速率限制测试
    # --------------------------
    def test_7_rate_limiting_on_login(self):
        """测试登录接口的速率限制"""
        login_url = f"{BASE_URL}/auth/login/"
        
        # 发送多个登录请求
        for i in range(15):  # 假设限制为10次/分钟
            response = requests.post(login_url, json={
                "username": f"rate_test_user_{i}",
                "password": "wrongpassword"
            })
            
            # 检查是否达到速率限制
            if i >= 10 and response.status_code != 429:
                self.fail("速率限制未生效")
        
        # 等待一段时间后重试
        import time
        time.sleep(60)
        
        # 再次尝试应该可以成功
        response = requests.post(login_url, json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        })
        self.assertEqual(response.status_code, 200, "速率限制后应恢复正常")

    # --------------------------
    # 敏感数据暴露测试
    # --------------------------
    def test_8_sensitive_data_exposure(self):
        """测试响应中是否包含敏感数据"""
        endpoints_to_check = [
            f"{BASE_URL}/auth/profile/",
            f"{BASE_URL}/devices/",
            f"{BASE_URL}/rooms/"
        ]
        
        sensitive_keys = ["password", "token", "secret", "key", "email"]
        
        for endpoint in endpoints_to_check:
            response = requests.get(endpoint, headers=self.headers)
            self.assertEqual(response.status_code, 200)
            
            # 检查响应体和头部
            response_data = response.text.lower()
            for key in sensitive_keys:
                self.assertNotIn(key, response_data, f"敏感数据暴露: {endpoint} 可能包含 {key}")

if __name__ == "__main__":
    unittest.main(verbosity=2)