from django.db import models
from django.contrib.auth.models import AbstractUser

class Room(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Device(models.Model):
    DEVICE_TYPES = [
        ('light', 'Light'),
        ('ac', 'Air Conditioner'),
        ('outlet', 'Outlet'),
        ('curtain', 'Curtain'),
        ('tv', 'Television'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='devices')
    status = models.BooleanField(default=False)
    extra = models.JSONField(default=dict) # 不同的设备有不同的属性，比如空调有温度属性

    def __str__(self):
        return f'{self.name} ({self.room.name})'

class Scene(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name

class SceneDeviceConfig(models.Model):
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE, related_name='device_configs')
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    status = models.BooleanField()
    config = models.JSONField(default=dict)

    def __str__(self):
        return f'{self.scene.name} - {self.device.name}'

class SmartHomeUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    permissions = models.JSONField(default=list)
