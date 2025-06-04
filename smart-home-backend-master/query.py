# import os
# import django

# # 设置 Django 环境变量
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartHomeBackend.settings')
# django.setup()  # 加载 Django 配置

# from core.models import Device, Room,SmartHomeUser

# # 示例：查询所有设备
# devices = SmartHomeUser.objects.all()
# for device in devices:
#     print(f"设备名: {device.username}, 状态: {device.password}")
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartHomeBackend.settings')
django.setup()

from core.models import SmartHomeUser

# 查询并打印所有用户
users = SmartHomeUser.objects.all()
print("===== 用户列表 =====")
for user in users:
    print(f"用户名: {user.username}, 角色: {user.role}, 活跃: {user.is_active}")