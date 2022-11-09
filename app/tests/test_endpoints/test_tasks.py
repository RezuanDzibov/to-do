from django.urls import reverse
from rest_framework.test import APIClient

from tasks import models, serializers


class TestCreateTask:
    def test_successful(self, auth_test_client: APIClient, built_task: models.Task):
        built_task_serializer = serializers.TaskCreateSerializerIn(built_task)
        response = auth_test_client.post(reverse("task-create"), built_task_serializer.data)
        assert response.status_code == 201
        assert response.data["id"]

    def test_unsuccessful(self, auth_test_client: APIClient, built_task: models.Task):
        built_task.title = "a" * 300
        built_task.available = "okoso"
        built_task_serializer = serializers.TaskCreateSerializerIn(built_task)
        response = auth_test_client.post(reverse("task-create"), built_task_serializer.data)
        assert response.status_code == 400

    def test_not_exists_related_id(self, auth_test_client: APIClient, built_task: models.Task):
        built_task.category = models.Category(id=8)
        built_task_serializer = serializers.TaskCreateSerializerIn(built_task)
        response = auth_test_client.post(reverse("task-create"), built_task_serializer.data)
        assert response.status_code == 400

    def test_not_auth(self, test_client: APIClient, built_task: models.Task):
        built_task_serializer = serializers.TaskCreateSerializerIn(built_task)
        response = test_client.post(reverse("task-create"), built_task_serializer.data)
        assert response.status_code == 401
