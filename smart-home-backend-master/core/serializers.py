from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import Room, Device, Scene, SceneDeviceConfig, SmartHomeUser
#模型默认都有 id 主键字段，即使你不写 id = models.AutoField(...)，Django 也会自动添加。这对于数据库操作、序列化、查找（如 get(id=...)）是必需的。
# Serializer（序列化器）是用于在模型（数据库对象）和 JSON 等格式之间进行转换

class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = SmartHomeUser
        fields = ['username', 'email', 'password', 'password_confirm', 'phone', 'nickname', 'role']
        extra_kwargs = {
            'email': {'required': False, 'allow_null': True},
            'phone': {'required': False, 'allow_null': True},
            'nickname': {'required': False},
            'role': {'read_only': True},  # 注册时默认为普通成员
        }
    
    def validate(self, attrs):
        """验证密码确认"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("两次输入的密码不一致")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        validated_data['role'] = 'member'  # 默认角色
        user = SmartHomeUser.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('用户名或密码错误')
            if not user.is_active:
                raise serializers.ValidationError('用户账户已被禁用')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('请提供用户名和密码')
        
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""
    class Meta:
        model = SmartHomeUser
        fields = ['id', 'email', 'phone', 'nickname', 'bio', 'avatar', 
                 'role', 'first_name', 'last_name', 'date_joined', 'last_login', 'created_at']
        read_only_fields = ['id', 'username', 'role', 'date_joined', 'last_login', 'created_at']

class UserUpdateSerializer(serializers.ModelSerializer):
    """用户信息更新序列化器"""
    class Meta:
        model = SmartHomeUser
        fields = ['id', 'email', 'phone', 'nickname', 'bio', 'avatar', 'first_name', 'last_name']
        read_only_fields = ['id']

class PasswordChangeSerializer(serializers.Serializer):
    """密码修改序列化器"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("两次输入的新密码不一致")
        return attrs

class SmartHomeUserSerializer(serializers.ModelSerializer):
    """完整的用户序列化器（用于管理员）"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = SmartHomeUser
        fields = ['id', 'username', 'email', 'password', 'phone', 'nickname', 'bio', 
                 'avatar', 'role', 'permissions', 'is_active', 'first_name', 'last_name',
                 'date_joined', 'last_login', 'created_at', 'updated_at']
        read_only_fields = ['id', 'date_joined', 'last_login', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = SmartHomeUser.objects.create_user(**validated_data)
        return user

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name']
        read_only_fields = ['id']

class DeviceSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    ip_address = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    #这是 Django/DRF 版本兼容性问题，显式声明 ip_address 字段并指定 protocol 可解决。
    class Meta:
        model = Device
        fields = ['id', 'name', 'type', 'room', 'status', 'extra', 'brand', 'owner', 'ip_address', 'port']
        read_only_fields = ['id', 'owner']

    def create(self, validated_data):
        # 确保owner字段不会冲突
        print("creating")
        validated_data.pop('owner', None)  # 移除可能存在的owner字段
        user = self.context['request'].user
        return Device.objects.create(owner=user, **validated_data)

class SceneDeviceConfigSerializer(serializers.ModelSerializer):
    device = serializers.PrimaryKeyRelatedField(queryset=Device.objects.all())

    class Meta:
        model = SceneDeviceConfig
        fields = ['device', 'status', 'config']

class SceneSerializer(serializers.ModelSerializer):
    device_configs = SceneDeviceConfigSerializer(many=True)

    class Meta:
        model = Scene
        fields = ['id', 'name', 'description', 'device_configs']
    
    def create(self, validated_data):
        print("creating scene")
        print(validated_data)
        device_configs_data = validated_data.pop('device_configs')
        scene = Scene.objects.create(**validated_data)
        for config_data in device_configs_data:
            SceneDeviceConfig.objects.create(scene=scene, **config_data)
        return scene

    def update(self, instance, validated_data):
        # 更新基本字段
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        # 更新设备配置：整体替换
        if 'device_configs' in validated_data:
            device_configs_data = validated_data.pop('device_configs')
            # 删除旧的配置
            instance.device_configs.all().delete()
            # 添加新的配置
            for config_data in device_configs_data:
                SceneDeviceConfig.objects.create(scene=instance, **config_data)
        return instance
