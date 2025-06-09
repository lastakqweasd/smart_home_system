from rest_framework import serializers
from .models import Room, Device, Scene, SceneDeviceConfig, SmartHomeUser
#模型默认都有 id 主键字段，即使你不写 id = models.AutoField(...)，Django 也会自动添加。这对于数据库操作、序列化、查找（如 get(id=...)）是必需的。
# Serializer（序列化器）是用于在模型（数据库对象）和 JSON 等格式之间进行转换

class SmartHomeUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # 禁止返回密码
    
    class Meta:
        model = SmartHomeUser
        fields = ['id', 'username', 'password', 'role']
    
    def create(self, validated_data):
        # 自动处理密码哈希
        user = SmartHomeUser.objects.create_user(**validated_data)
        return user

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name']

class DeviceSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())  #引用room，是一个外键，需要传id进去
    #room_id = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), source='room', write_only=True)
    class Meta:
        model = Device
        fields = ['id', 'name', 'type', 'room', 'status', 'extra', 'brand']

class SceneDeviceConfigSerializer(serializers.ModelSerializer):
    device = serializers.PrimaryKeyRelatedField(queryset=Device.objects.all())  #在 JSON 中，你希望通过设备的主键 ID 来表示设备
    #device_id = serializers.PrimaryKeyRelatedField(queryset=Device.objects.all(), source='device', write_only=True)

    class Meta:
        model = SceneDeviceConfig
        # 这几个字段分别表示设备的id/状态/需要调整到的配置（比如多少度）
        fields = ['device', 'status', 'config']

class SceneSerializer(serializers.ModelSerializer):
    device_configs = SceneDeviceConfigSerializer(many=True)

    class Meta:
        model = Scene
        fields = ['id', 'name', 'description', 'device_configs']
    #device_configs是可写的嵌套字段，Django REST Framework 不会自动帮你保存 device_configs，你必须手动实现 create() 方法。
    def create(self, validated_data):
        device_configs_data = validated_data.pop('device_configs') #从 validated_data（即经过校验的数据）中取出键为 'device_configs' 的值，并从字典中删除这个键。
        # device_configs_data包含了所有设备配置的列表，每个配置都是一个字典，包含 device_id、status 和 config 字段。
        scene = Scene.objects.create(**validated_data)  #用剩下的字段（name、description）创建一个新的 Scene 实例。
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
