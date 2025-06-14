from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid

class Room(models.Model):
    id = models.CharField(primary_key=True, max_length=64, default= str(uuid.uuid4()), editable=False)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class SmartHomeUser(AbstractUser):
    # id = models.CharField(primary_key=True, max_length=64, default= str(uuid.uuid4()), editable=False)
    # 替换继承的id字段
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,  # 注意：去掉了括号，传递函数而非固定值
        editable=False,
        db_index=True
    )
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('member', '普通成员'),
        ('guest', '访客'),
    ]
    
    # 基本信息
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member', verbose_name='用户角色')
    email = models.EmailField(unique=False, verbose_name='邮箱')
    phone_regex = RegexValidator(
        regex=r'^1[3-9]\d{9}$',
        message="手机号格式不正确，请输入11位数字"
    )
    phone = models.CharField(validators=[phone_regex], max_length=11, blank=True, null=True, verbose_name='手机号')
    
    # 个人信息
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    nickname = models.CharField(max_length=50, blank=True, null=True, verbose_name='昵称')
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name='个人简介')
    
    # 系统信息
    permissions = models.JSONField(default=list, verbose_name='权限列表')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    last_login_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name='最后登录IP')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '智能家居用户'
        verbose_name_plural = '智能家居用户'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'
    
    def has_permission(self, permission):
        """检查用户是否有特定权限"""
        if self.role == 'admin':
            return True
        return permission in self.permissions

class Device(models.Model):
    id = models.CharField(primary_key=True, max_length=64, default= str(uuid.uuid4()), editable=False)
    DEVICE_TYPES = [
        ('light', 'Light'),
        ('ac', 'Air Conditioner'),
        ('outlet', 'Outlet'),
        ('curtain', 'Curtain'),
        ('tv', 'Television'),
    ]

    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='devices')
    status = models.BooleanField(default=False)
    extra = models.JSONField(default=dict) # 不同的设备有不同的属性，比如空调有温度属性
    owner = models.ForeignKey(SmartHomeUser, on_delete=models.CASCADE, related_name='devices', null=True, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='设备IP地址')
    port = models.PositiveIntegerField(blank=True, null=True, verbose_name='设备端口')

    def __str__(self):
        return f'{self.name} ({self.room.name})'

class Scene(models.Model):
    id = models.CharField(primary_key=True, max_length=64, default=str(uuid.uuid4()), editable=False)
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name

class SceneDeviceConfig(models.Model):
    id = models.CharField(primary_key=True, max_length=64, default= str(uuid.uuid4()), editable=False)
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE, related_name='device_configs')
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    status = models.BooleanField()
    config = models.JSONField(default=dict)

    def __str__(self):
        return f'{self.scene.name} - {self.device.name}'
