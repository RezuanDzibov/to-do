from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import get_upload_path


class User(AbstractUser):
    avatar = models.ImageField(upload_to=get_upload_path, blank=True, null=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
