from django.contrib.auth.models import AbstractUser
from django.db import models

from app.common.models import Image


class AvatarImage(Image):
    date_uploaded = models.DateField(auto_now=True)

    class Meta:
        verbose_name = "Avatar"
        verbose_name_plural = "Avatars"


class User(AbstractUser):
    avatar = models.OneToOneField(AvatarImage, on_delete=models.DO_NOTHING, null=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
