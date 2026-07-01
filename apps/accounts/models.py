from django.contrib.auth.models import AbstractUser
from django.db import models


def avatar_upload_to(instance, filename: str) -> str:
    return f"avatars/{instance.pk or 'new'}/{filename}"


class User(AbstractUser):
    """Custom user model.

    Inherits the full Django auth stack (username login, permissions, groups)
    and adds a few common profile fields. This is the model you edit per
    project — add columns, add a custom manager, switch USERNAME_FIELD to
    email/phone, etc. Because AUTH_USER_MODEL points here from day one, those
    changes are cheap.
    """

    phone = models.CharField(max_length=20, blank=True, db_index=True)
    display_name = models.CharField(max_length=150, blank=True)
    # Uploaded profile image (stored on B2 when configured, else locally).
    avatar = models.ImageField(upload_to=avatar_upload_to, blank=True, null=True)
    # External profile image link (e.g. an OAuth/CDN avatar URL).
    profile_image_url = models.URLField(max_length=500, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.get_username()
