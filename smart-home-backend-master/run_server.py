import os
import threading
import django

# 初始化 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartHomeBackend.settings')
django.setup()

from core.tcp_server import start_tcp_server
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    # 只在主进程中启动 TCP 服务
    if os.environ.get('RUN_MAIN') != 'true':
        if start_tcp_server(port=9000):
            print("TCP服务启动成功")
        else:
            print("TCP服务启动失败")

    # 启动 Django
    execute_from_command_line(['manage.py', 'runserver', '172.20.10.3:8000'])
