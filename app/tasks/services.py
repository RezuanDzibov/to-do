from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import exceptions

from tasks import models
from tasks import serializers

User = get_user_model()


def create_task(user: User, data: dict) -> models.Task:
    task_serializer = serializers.TaskCreateSerializerIn(data=data)
    task_serializer.is_valid(raise_exception=True)
    task_data = task_serializer.validated_data
    task = models.Task(user=user, **task_data)
    task.save()
    return task


def get_task(id_: int) -> models.Task:
    task = get_object_or_404(models.Task, id=id_)
    return task


def delete_task(user: User, id_: int) -> None:
    task = get_object_or_404(models.Task, id=id_, user=user)
    task.delete()


def update_task(user: User, id_: int, data: dict) -> models.Task:
    task = models.Task.objects.filter(id=id_)
    if not task:
        raise exceptions.NotFound()
    if user.id != task[0].user.id:
        raise exceptions.PermissionDenied()
    try:
        task.update(**data)
    except FieldDoesNotExist as exception:
        raise exceptions.ValidationError(detail=exception.args[0])
    task = task[0]
    return task


def create_task_image(user: User, data: dict) -> models.TaskImage:
    task_image_serializer = serializers.TaskImageCreateSerializer(data=data)
    task_image_serializer.is_valid(raise_exception=True)
    task_image_data = task_image_serializer.validated_data
    task = get_object_or_404(models.Task, id=task_image_data["task"].id)
    if user.id != task.user.id:
        raise exceptions.PermissionDenied()
    task_image = models.TaskImage.objects.create(**task_image_data)
    return task_image


def get_task_image(task_image_id: int) -> models.TaskImage:
    task_image = get_object_or_404(models.TaskImage, id=task_image_id)
    return task_image


def delete_task_image(user: models.User, task_image_id) -> None:
    try:
        task_image = models.TaskImage.objects.get(id=task_image_id)
    except models.TaskImage.DoesNotExist:
        raise exceptions.NotFound()
    if task_image.task.user.pk != user.id:
        raise exceptions.PermissionDenied
    task_image.delete()
