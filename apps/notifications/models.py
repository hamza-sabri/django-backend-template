from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class DeviceToken(TimeStampedModel):
    """An FCM registration token for one of a user's devices.

    Clients register their token here; sending helpers in `fcm.py` look these
    up to deliver push notifications. Dead/unregistered tokens are auto-marked
    inactive after a failed send.
    """

    class Platform(models.TextChoices):
        ANDROID = "android", "Android"
        IOS = "ios", "iOS"
        WEB = "web", "Web"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="device_tokens",
    )
    token = models.CharField(max_length=255, unique=True, db_index=True)
    platform = models.CharField(max_length=10, choices=Platform.choices, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "device_tokens"
        verbose_name = "Device token"
        verbose_name_plural = "Device tokens"

    def __str__(self) -> str:
        return f"{self.user} · {self.platform or 'device'}"
