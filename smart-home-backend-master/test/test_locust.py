from locust import HttpUser, task, between
import random
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    filename='locust_tests.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class QuickstartUser(HttpUser):
    wait_time = between(1, 2.5)
    host = "http://localhost:8000/api"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.user_id = None
        # 使用类变量存储测试账号信息，确保所有用户实例使用相同的测试账号
        self.test_username = f"testuser_{random.randint(1, 100000)}"
        self.test_email = f"test_{random.randint(1, 100000)}@example.com"
        self.test_password = "testpass123"
    
    def on_start(self):
        """每个用户开始运行时首先执行注册"""
        self.register_user()
    
    @task(3)
    def register_user(self):
        data = {
            "username": self.test_username,
            "email": self.test_email,
            "password": self.test_password,
            "password_confirm": self.test_password,
            "phone": "138" + str(random.randint(10000000, 99999999)),
            "nickname": f"测试用户_{random.randint(1, 100000)}"
        }
        
        try:
            with self.client.post("/auth/register/", json=data, catch_response=True) as response:
                if response.status_code == 201:
                    self.token = response.json().get('tokens', {}).get('access')
                    self.user_id = response.json().get('user', {}).get('id')
                    response.success()
                    logger.info(f"用户注册成功 - 用户名: {self.test_username}, 用户ID: {self.user_id}")
                else:
                    error_msg = f"注册失败 - 状态码: {response.status_code}, 响应: {response.text}"
                    response.failure(error_msg)
                    logger.error(error_msg)
        except Exception as e:
            error_msg = f"注册请求异常: {str(e)}"
            logger.exception(error_msg)
            response.failure(error_msg)
    
    @task(2)
    def login_user(self):
        # 使用注册时创建的账号登录
        data = {
            "username": self.test_username,
            "password": self.test_password
        }
        
        try:
            with self.client.post("/auth/login/", json=data, catch_response=True) as response:
                if response.status_code == 200:
                    self.token = response.json().get('tokens', {}).get('access')
                    self.user_id = response.json().get('user', {}).get('id')
                    response.success()
                    logger.info(f"用户登录成功 - 用户ID: {self.user_id}")
                else:
                    error_msg = f"登录失败 - 状态码: {response.status_code}, 响应: {response.text}"
                    response.failure(error_msg)
                    logger.error(error_msg)
        except Exception as e:
            error_msg = f"登录请求异常: {str(e)}"
            logger.exception(error_msg)
            response.failure(error_msg)
    
    @task(1)
    def get_profile(self):
        if not self.token:
            logger.warning("尝试获取用户信息但未检测到token，跳过此请求")
            return
            
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        try:
            with self.client.get("/auth/profile/", headers=headers, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                    logger.info(f"成功获取用户信息 - 用户ID: {self.user_id}")
                else:
                    error_msg = f"获取用户信息失败 - 状态码: {response.status_code}, 响应: {response.text}"
                    response.failure(error_msg)
                    logger.error(error_msg)
        except Exception as e:
            error_msg = f"获取用户信息请求异常: {str(e)}"
            logger.exception(error_msg)
            response.failure(error_msg)