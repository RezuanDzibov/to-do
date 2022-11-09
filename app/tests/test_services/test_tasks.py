import pytest
from django.contrib.auth import get_user_model
from rest_framework import exceptions

from tasks import models, services, serializers

User = get_user_model()


class TestCreate:
    def test_success(self, admin_user: User, built_task: models.Task):
        task_serializer = serializers.TaskCreateSerializerIn(built_task)
        created_task = services.create_task(user=admin_user, data=task_serializer.data)
        assert task_serializer.data == serializers.TaskCreateSerializerIn(created_task).data

    def test_unsuccessful(self, admin_user: User, built_task: models.Task):
        built_task.title = "a" * 300
        built_task.available = None
        task_serializer = serializers.TaskCreateSerializerIn(built_task)
        with pytest.raises(exceptions.ValidationError) as exception:
            services.create_task(user=admin_user, data=task_serializer.data)
        assert exception.value.status_code == 400

    def test_not_exists_related_id(self, admin_user: User, built_task: models.Task):
        built_task.category = models.Category(id=8)
        task_serializer = serializers.TaskCreateSerializerIn(built_task)
        with pytest.raises(exceptions.ValidationError) as exception:
            services.create_task(user=admin_user, data=task_serializer.data)
        assert exception.value.status_code == 400
