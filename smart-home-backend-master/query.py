# # import os
# # import django

# # # 设置 Django 环境变量
# # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartHomeBackend.settings')
# # django.setup()  # 加载 Django 配置

# # from core.models import Device, Room,SmartHomeUser

# # # 示例：查询所有设备
# # devices = SmartHomeUser.objects.all()
# # for device in devices:
# #     print(f"设备名: {device.username}, 状态: {device.password}")
# import os
# import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartHomeBackend.settings')
# django.setup()

# from core.models import SmartHomeUser

# # 查询并打印所有用户
# users = SmartHomeUser.objects.all()
# print("===== 用户列表 =====")
# for user in users:
#     print(f"用户名: {user.username}, 角色: {user.role}, 活跃: {user.is_active}")

# import sqlite3

# # 连接数据库
# conn = sqlite3.connect('db.sqlite3')
# cursor = conn.cursor()

# # 获取设备表数据
# cursor.execute("SELECT * FROM core_device")
# print(cursor.fetchall())

# # 关闭连接
# conn.close()

import sqlite3

# 连接数据库
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# 查询表的字段信息（假设表名为 core_device）
cursor.execute("PRAGMA table_info(core_device)")
columns = cursor.fetchall()

# 打印字段详情
print("字段列表：")
for col in columns:
    print(f"""
    字段名: {col[1]}
    数据类型: {col[2]}
    是否允许NULL: {'是' if col[3] else '否'}
    默认值: {col[4]}
    是否主键: {'是' if col[5] else '否'}
    """)

# 关闭连接
conn.close()