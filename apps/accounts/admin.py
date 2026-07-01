from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        "username",
        "email",
        "phone",
        "display_name",
        "is_staff",
        "is_active",
        "date_joined",
    )
    search_fields = ("username", "email", "phone", "display_name")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Profile", {"fields": ("phone", "display_name", "avatar", "profile_image_url")}),
    )
