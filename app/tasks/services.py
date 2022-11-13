from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

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
