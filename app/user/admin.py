from django.contrib import admin
from django.contrib.admin import register

from .models import User


@register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_active")
    list_filter = ("is_active", "is_staff", "is_superuser")
    list_display_links = ("username", "email")

