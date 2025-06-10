# api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    DeviceViewSet, RoomViewSet, SceneViewSet, SmartHomeUserViewSet,
    RegisterView, LoginView, LogoutView, UserProfileView, PasswordChangeView
)

router = DefaultRouter()
router.register(r'devices', DeviceViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'scenes', SceneViewSet)
router.register(r'users', SmartHomeUserViewSet)

urlpatterns = [
    # 用户认证相关
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 用户资料管理
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    path('auth/change-password/', PasswordChangeView.as_view(), name='change_password'),
    
    # API路由
    path('', include(router.urls)),
]
