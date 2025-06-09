# api/views.py

import json
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate

from .models import Device, Room, Scene, SceneDeviceConfig,SmartHomeUser
from .serializers import DeviceSerializer, RoomSerializer, SceneSerializer,SmartHomeUserSerializer
from .controller import DeviceController

#定义了你 Django 后端的三个视图类（ViewSets），分别用于 设备（Device）、房间（Room） 和 场景（Scene） 的增删改查 API 接口

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            return Response({
                'success': True,
                'user_id': user.id,
                'username': user.username,
                'role': user.role
            }, status=status.HTTP_200_OK)
        return Response({'error': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)

class SmartHomeUserViewSet(viewsets.ModelViewSet):
    queryset = SmartHomeUser.objects.all()
    serializer_class = SmartHomeUserSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    # 创建设备后自动发送控制命令
    def perform_create(self, serializer):
        device = serializer.save()
        DeviceController.control(device)  # 或 control(device)，视你的 controller 命名而定

    # 更新设备后也发送控制命令（你已有）
    def perform_update(self, serializer):
        device = serializer.save()
        DeviceController.control(device)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class SceneViewSet(viewsets.ModelViewSet):
    queryset = Scene.objects.all()
    serializer_class = SceneSerializer

    #你添加了一个自定义接口 /api/scenes/{id}/activate/，前端可以通过 POST 请求激活某个场景
    #@action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    @action(detail=True, methods=['post'], permission_classes=[])
    def activate(self, request, pk=None):
        try:
            scene = self.get_object()
            for config in scene.device_configs.all():
                device = config.device
                device.status = config.status
                device.extra.update(config.config)
                device.save()

                DeviceController.control(device)
            return Response({'message': f'场景【{scene.name}】已激活'})
        except Scene.DoesNotExist:
            return Response({'error': '场景不存在'}, status=status.HTTP_404_NOT_FOUND)
