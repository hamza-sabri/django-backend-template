from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from . import fcm
from .models import DeviceToken
from .serializers import DeviceTokenSerializer, SendNotificationSerializer

User = get_user_model()


class DeviceTokenViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Register / list / remove the current user's device tokens.

    POST /api/v1/notifications/devices/   -> register (upsert) a token
    GET  /api/v1/notifications/devices/   -> list your tokens
    DELETE .../devices/{id}/              -> remove one
    """

    serializer_class = DeviceTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeviceToken.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj, _ = DeviceToken.objects.update_or_create(
            token=serializer.validated_data["token"],
            defaults={
                "user": request.user,
                "platform": serializer.validated_data.get("platform", ""),
                "is_active": True,
            },
        )
        return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)


class SendNotificationView(APIView):
    """Admin: send a push to one user (`user_id`) or everyone (omit it).

    No-ops with `{"enabled": false}` when FCM isn't configured.
    """

    permission_classes = [permissions.IsAdminUser]
    serializer_class = SendNotificationSerializer

    @extend_schema(request=SendNotificationSerializer, responses={200: dict})
    def post(self, request):
        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        title, body = data["title"], data["body"]
        payload = data.get("data")

        if data.get("user_id"):
            user = User.objects.filter(pk=data["user_id"]).first()
            if not user:
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            result = fcm.send_to_user(user, title, body, payload)
        else:
            result = fcm.send_to_all(title, body, payload)
        return Response(result)
