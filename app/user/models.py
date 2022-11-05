from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import Image


class AvatarImage(Image):
    upload_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Avatar"
        verbose_name_plural = "Avatars"


class User(AbstractUser):
    avatar = models.OneToOneField(AvatarImage, on_delete=models.DO_NOTHING, null=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
