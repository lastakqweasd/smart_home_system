# api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceViewSet, RoomViewSet, SceneViewSet,SmartHomeUserViewSet,LoginView

router = DefaultRouter()
router.register(r'devices', DeviceViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'scenes', SceneViewSet)
router.register(r'users', SmartHomeUserViewSet)

urlpatterns = [
    path(r'login', LoginView.as_view()),  # 新增登录路由
    path('', include(router.urls)),
]
