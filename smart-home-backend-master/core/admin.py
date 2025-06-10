from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import SmartHomeUser, Room, Device, Scene, SceneDeviceConfig

@admin.register(SmartHomeUser)
class SmartHomeUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_active', 'date_joined', 'last_login']
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'nickname']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('email', 'phone', 'nickname', 'bio', 'avatar')}),
        ('权限', {'fields': ('role', 'permissions', 'is_active', 'is_staff', 'is_superuser')}),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'room', 'status', 'owner']
    list_filter = ['type', 'status', 'room']
    search_fields = ['name', 'brand']
    ordering = ['name']

@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(SceneDeviceConfig)
class SceneDeviceConfigAdmin(admin.ModelAdmin):
    list_display = ['scene', 'device', 'status']
    list_filter = ['scene', 'device', 'status']
