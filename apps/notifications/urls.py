from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"notifications/devices", views.DeviceTokenViewSet, basename="device-token")

urlpatterns = router.urls + [
    path("notifications/send/", views.SendNotificationView.as_view(), name="notification-send"),
]
