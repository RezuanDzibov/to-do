from django.contrib.auth import get_user_model

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
