import random
from typing import List

import pytest
from django.contrib.auth import get_user_model
from django.forms import model_to_dict
from django.http import response, Http404
from rest_framework import exceptions

from tasks import models, services, serializers

User = get_user_model()


class TestTaskCreate:
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


class TestGetTask:
    def test_success(self, admin_user: User, task: models.Task):
        task_in_db = services.get_task(id_=task.id)
        assert task == task_in_db

    def test_not_exist(self, db):
        with pytest.raises(response.Http404):
            services.get_task(id_=random.randint(1, 10))


class TestDeleteTask:
    def test_success(self, admin_user: User, task: models.Task):
        services.delete_task(user=admin_user, id_=task.id)
        with pytest.raises(models.Task.DoesNotExist):
            models.Task.objects.get(id=task.id)

    def test_success_with_multiple_tasks(self, admin_user: User, tasks: List[models.Task]):
        task = random.choice(tasks)
        services.delete_task(user=admin_user, id_=task.id)
        with pytest.raises(models.Task.DoesNotExist):
            models.Task.objects.get(id=task.id)

    def test_with_not_author(self, user_and_its_password: dict, task: models.Task):
        with pytest.raises(Http404):
            services.delete_task(user=user_and_its_password["user"], id_=task.id)

    @pytest.mark.parametrize("tasks", [7], indirect=True)
    def test_not_exist_task(self, admin_user: User, tasks: List[models.Task]):
        with pytest.raises(Http404):
            services.delete_task(user=admin_user, id_=random.randint(100, 200))

    def test_not_exist_task_without_tasks(self, admin_user: User):
        with pytest.raises(Http404):
            services.delete_task(user=admin_user, id_=1)


class TestTaskUpdate:
    def test_success(self, admin_user: User, task: models.Task):
        data_for_update = {"title": "another", "available": False}
        task = services.update_task(user=admin_user, id_=task.id, data=data_for_update)
        assert task.title == data_for_update["title"] and task.available == data_for_update["available"]

    def test_with_multiple_tasks(self, admin_user: User, tasks: List[models.Task]):
        data_for_update = {"title": "another", "available": False}
        task = services.update_task(user=admin_user, id_=random.choice(tasks).id, data=data_for_update)
        assert task.title == data_for_update["title"] and task.available == data_for_update["available"]

    def test_invalid_data(self, admin_user: User, task: models.Task):
        data_for_update = {"some": "another", "another_some": "some"}
        with pytest.raises(exceptions.ValidationError):
            services.update_task(user=admin_user, id_=task.id, data=data_for_update)

    def test_not_author(self, user_and_its_password: User, task: models.Task):
        data_for_update = {"title": "another", "available": False}
        with pytest.raises(exceptions.PermissionDenied):
            services.update_task(user=user_and_its_password["user"], id_=task.id, data=data_for_update)

    def test_not_exist_task(self, admin_user: User):
        data_for_update = {"title": "another", "available": False}
        with pytest.raises(exceptions.NotFound):
            services.update_task(user=admin_user, id_=random.randint(1, 100), data=data_for_update)


class TestCreateTaskImage:
    def test_success(self, admin_user: User, tasks: List[models.Task], built_task_image: models.TaskImage):
        task = random.choice(tasks)
        data_for_create = {k: v for k, v in model_to_dict(built_task_image).items() if v is not None}
        data_for_create["task"] = task.id
        task_image = services.create_task_image(user=admin_user, data=data_for_create)
        assert task_image
        assert task_image.id
        assert task_image.task.id == task.id

    def test_unsuccessful(self, admin_user: User, tasks: List[models.Task], built_task_image: models.TaskImage):
        task = random.choice(tasks)
        data_for_create = {k: v for k, v in model_to_dict(built_task_image).items() if v is not None}
        data_for_create["task"] = task.id
        data_for_create["title"] = "a" * 300
        with pytest.raises(exceptions.ValidationError) as exception:
            services.create_task_image(user=admin_user, data=data_for_create)
        assert exception.value.status_code == 400

    def test_not_exists_related_id(self, admin_user: User, built_task_image: models.TaskImage):
        data_for_create = {k: v for k, v in model_to_dict(built_task_image).items() if v is not None}
        data_for_create["task"] = 20
        with pytest.raises(exceptions.ValidationError) as exception:
            services.create_task_image(user=admin_user, data=data_for_create)
        assert exception.value.status_code == 400


class TestRetrieveTaskImage:
    def test_success(self, task_images: List[models.TaskImage]):
        task_image = random.choice(task_images)
        task_image_in_db = services.get_task_image(task_image_id=task_image.id)
        assert task_image == task_image_in_db

    def test_not_exists(self, task_images: List[models.TaskImage]):
        with pytest.raises(Http404):
            services.get_task_image(task_image_id=random.randint(100, 200))

    def test_not_any_exist(self, db):
        with pytest.raises(Http404):
            services.get_task_image(task_image_id=1)
