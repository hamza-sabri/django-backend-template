from rest_framework import serializers

from .models import DeviceToken


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ["id", "token", "platform", "is_active", "created_at"]
        read_only_fields = ["id", "is_active", "created_at"]
        # Re-registering the same token is an upsert (handled in the view), so
        # drop the default unique validator that would reject it.
        extra_kwargs = {"token": {"validators": []}}


class SendNotificationSerializer(serializers.Serializer):
    title = serializers.CharField()
    body = serializers.CharField()
    data = serializers.DictField(
        required=False, help_text="Optional key/value payload delivered with the push."
    )
    user_id = serializers.IntegerField(
        required=False, help_text="Send to this user only. Omit to send to everyone."
    )
