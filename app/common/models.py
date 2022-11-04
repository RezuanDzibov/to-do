import datetime
from typing import Type

from django.db import models


def get_upload_path(instance: Type[models.Model], filename: str):
    """Construct image path"""
    return f"{instance.__class__.__name__.lower()}/{'/'.join(str(datetime.date.today()).split('-'))}/{filename}"


class Image(models.Model):
    image = models.ImageField(upload_to=get_upload_path)

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"
        abstract = True
