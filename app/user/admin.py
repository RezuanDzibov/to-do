from django.contrib import admin
from django.contrib.admin import register

from .models import AvatarImage, User


@register(AvatarImage)
class AvatarImageAdmin(admin.ModelAdmin):
    pass


@register(User)
class UserAdmin(admin.ModelAdmin):
    pass
