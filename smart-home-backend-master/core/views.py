# api/views.py

import json
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Device, Room, Scene, SceneDeviceConfig, SmartHomeUser
from .serializers import (
    DeviceSerializer, RoomSerializer, SceneSerializer, SmartHomeUserSerializer,
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserUpdateSerializer, PasswordChangeSerializer
)
from .controller import DeviceController

#定义了你 Django 后端的三个视图类（ViewSets），分别用于 设备（Device）、房间（Room） 和 场景（Scene） 的增删改查 API 接口

class RegisterView(APIView):
    """用户注册视图"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        print(f"收到注册请求数据: {request.data}")
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': '注册成功',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)
        print(f"验证失败: {serializer.errors}")
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """用户登录视图"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # 更新最后登录时间和IP
            user.last_login = timezone.now()
            user.last_login_ip = self.get_client_ip(request)
            user.save()
            
            # 生成JWT令牌
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': '登录成功',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    # 'full_name': user.full_name
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class LogoutView(APIView):
    """用户注销视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'success': True,
                'message': '注销成功'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': '注销失败'
            }, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    """用户资料视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取用户资料"""
        serializer = UserProfileSerializer(request.user)
        return Response({
            'success': True,
            'user': serializer.data
        })
    
    def put(self, request):
        """更新用户资料"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': '资料更新成功',
                'user': UserProfileSerializer(request.user).data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(APIView):
    """密码修改视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            # 验证旧密码
            if not user.check_password(old_password):
                return Response({
                    'success': False,
                    'message': '原密码错误'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 设置新密码
            user.set_password(new_password)
            user.save()
            
            return Response({
                'success': True,
                'message': '密码修改成功'
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class SmartHomeUserViewSet(viewsets.ModelViewSet):
    """用户管理视图集（管理员专用）"""
    queryset = SmartHomeUser.objects.all()
    serializer_class = SmartHomeUserSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = SmartHomeUser.objects.all()
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)
        return queryset
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """激活用户"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({
            'success': True,
            'message': f'用户 {user.username} 已激活'
        })
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """禁用用户"""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({
            'success': True,
            'message': f'用户 {user.username} 已禁用'
        })

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print("asdqdqwdqw")
        user = self.request.user
        print(self.request)
        print(user)
        if user.role == 'admin':
            return Device.objects.all()
        return Device.objects.filter(owner=user)

    def perform_create(self, serializer):
        device = serializer.save()  # 序列化器已经设置了owner
        DeviceController.control(device)

    def perform_update(self, serializer):
        device = serializer.save()
        DeviceController.control(device)

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

class SceneViewSet(viewsets.ModelViewSet):
    queryset = Scene.objects.all()
    serializer_class = SceneSerializer
    permission_classes = [IsAuthenticated]

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
