import random
from typing import List

import pytest
from django.contrib.auth import get_user_model
from django.forms import model_to_dict
from django.urls import reverse
from rest_framework.test import APIClient

from tasks import models, serializers

User = get_user_model()


class TestCreateTask:
    def test_successful(self, admin_test_client, built_task: models.Task):
        built_task_serializer = serializers.TaskCreateSerializerIn(built_task)
        response = admin_test_client.post(reverse("task-create"), built_task_serializer.data)
        assert response.status_code == 201
        assert response.data["id"]

    def test_unsuccessful(self, admin_test_client, built_task: models.Task):
        built_task.title = "a" * 300
        built_task.available = "okoso"
        built_task_serializer = serializers.TaskCreateSerializerIn(built_task)
        response = admin_test_client.post(reverse("task-create"), built_task_serializer.data)
        assert response.status_code == 400

    def test_not_exists_related_id(self, admin_test_client, built_task: models.Task):
        built_task.category = models.Category(id=8)
        built_task_serializer = serializers.TaskCreateSerializerIn(built_task)
        response = admin_test_client.post(reverse("task-create"), built_task_serializer.data)
        assert response.status_code == 400

    def test_not_auth(self, test_client: APIClient, built_task: models.Task):
        built_task_serializer = serializers.TaskCreateSerializerIn(built_task)
        response = test_client.post(reverse("task-create"), built_task_serializer.data)
        assert response.status_code == 401


class TestTaskRetrieve:
    def test_success(self, task: models.Task, admin_test_client):
        response = admin_test_client.get(reverse("task-retrieve", kwargs={"task_id": task.id}))
        assert response.status_code == 200

    def test_not_exist(self, admin_test_client):
        response = admin_test_client.get(reverse("task-retrieve", kwargs={"task_id": random.randint(1, 10)}))
        assert response.status_code == 404

    @pytest.mark.parametrize("task", [{"available": True}], indirect=True)
    def test_task_available_true_not_auth_user(self, task: models.Task, client: APIClient):
        response = client.get(reverse("task-retrieve", kwargs={"task_id": task.id}))
        assert response.status_code == 200

    @pytest.mark.parametrize("task", [{"available": False}], indirect=True)
    def test_task_available_false_not_auth_user(self, task: models.Task, client: APIClient):
        response = client.get(reverse("task-retrieve", kwargs={"task_id": task.id}))
        assert response.status_code == 403


class TestTaskList:
    def test_success(self, admin_test_client, tasks: List[models.Task]):
        response = admin_test_client.get(reverse("task-list"))
        assert response.status_code == 200
        assert len(response.data) == len(tasks)

    def test_success_not_auth_user(self, test_client: APIClient, tasks: List[models.Task]):
        response = test_client.get(reverse("task-list"))
        assert response.status_code == 200
        assert len(response.data) == len(tasks)

    def test_available_is_true(self, admin_test_client, tasks: List[models.Task]):
        available_tasks = list(filter(lambda obj: obj.available is True, tasks))
        response = admin_test_client.get(f"{reverse('task-list')}?available=true")
        assert response.status_code == 200
        assert len(response.data) == len(available_tasks)
        assert all(task["available"] for task in response.data)

    def test_available_is_false(self, admin_test_client, tasks: List[models.Task]):
        available_tasks = list(filter(lambda obj: obj.available is False, tasks))
        response = admin_test_client.get(f"{reverse('task-list')}?available=false")
        assert response.status_code == 200
        assert len(response.data) == len(available_tasks)
        assert not all(task["available"] for task in response.data)

    def test_category_filter(
            self,
            admin_test_client,
            admin_user: User,
            tasks: List[models.Task],
            built_task: models.Task
    ):
        built_task.category = models.Category.objects.create(name="category")
        built_task.user = admin_user
        built_task.save()
        response = admin_test_client.get(f"{reverse('task-list')}?category__name=category")
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_status_filter(
            self,
            admin_test_client,
            admin_user: User,
            tasks: List[models.Task],
            built_task: models.Task
    ):
        built_task.status = models.Status.objects.create(name="status")
        built_task.user = admin_user
        built_task.save()
        response = admin_test_client.get(f"{reverse('task-list')}?status__name=status")
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_not_exist(self, admin_test_client):
        response = admin_test_client.get(reverse("task-list"))
        assert response.status_code == 200
        assert len(response.data) == 0


class TestDeleteTask:
    def test_success(self, admin_test_client, task: models.Task):
        response = admin_test_client.delete(reverse("task-delete", kwargs={"task_id": task.id}))
        assert response.status_code == 204
        with pytest.raises(models.Task.DoesNotExist):
            models.Task.objects.get(id=task.id)

    def test_success_with_multiple_tasks(self, admin_test_client, tasks: List[models.Task]):
        task = random.choice(tasks)
        response = admin_test_client.delete(reverse("task-delete", kwargs={"task_id": task.id}))
        assert response.status_code == 204
        with pytest.raises(models.Task.DoesNotExist):
            models.Task.objects.get(id=task.id)

    def test_with_not_author(self, user_test_client: APIClient, task: models.Task):
        response = user_test_client.delete(reverse("task-delete", kwargs={"task_id": task.id}))
        assert response.status_code == 404

    @pytest.mark.parametrize("tasks", [7], indirect=True)
    def test_not_exist_task(self, admin_test_client, tasks: List[models.Task]):
        response = admin_test_client.delete(reverse("task-delete", kwargs={"task_id": 100}))
        assert response.status_code == 404

    def test_not_exist_task_without_tasks(self, admin_test_client):
        response = admin_test_client.delete(reverse("task-delete", kwargs={"task_id": 1}))
        assert response.status_code == 404

    def test_without_user(self, test_client: APIClient, tasks: List[models.Task]):
        response = test_client.delete(reverse("task-delete", kwargs={"task_id": random.choice(tasks).id}))
        assert response.status_code == 401


class TestTaskUpdate:
    def test_success(self, admin_test_client, task: models.Task):
        data_for_update = {"title": "another", "available": False}
        response = admin_test_client.put(reverse("task-update", kwargs={"task_id": task.id}), data_for_update)
        assert response.status_code == 200
        assert response.data["title"] == data_for_update["title"] and response.data["available"] == data_for_update["available"]

    def test_with_multiple_tasks(self, admin_test_client, tasks: List[models.Task]):
        data_for_update = {"title": "another", "available": False}
        response = admin_test_client.put(
            reverse("task-update", kwargs={"task_id": random.choice(tasks).id}),
            data_for_update,
        )
        assert response.status_code == 200
        assert response.data["title"] == data_for_update["title"] and response.data["available"] == data_for_update["available"]

    def test_invalid_data(self, admin_test_client, task: models.Task):
        data_for_update = {"some": "another", "another_some": "some"}
        response = admin_test_client.put(
            reverse("task-update", kwargs={"task_id": task.id}),
            data_for_update,
        )
        assert response.status_code == 400

    def test_not_author(self, user_test_client: APIClient, task: models.Task):
        data_for_update = {"title": "another", "available": False}
        response = user_test_client.put(
            reverse("task-update", kwargs={"task_id": task.id}),
            data_for_update,
        )
        assert response.status_code == 403

    def test_not_exist_task(self, admin_test_client):
        data_for_update = {"title": "another", "available": False}
        response = admin_test_client.put(
            reverse("task-update", kwargs={"task_id": random.randint(1, 100)}),
            data_for_update,
        )
        assert response.status_code == 404

    def test_without_auth(self, test_client: APIClient, tasks: List[models.Task]):
        data_for_update = {"title": "another", "available": False}
        response = test_client.put(
            reverse("task-update", kwargs={"task_id": random.randint(1, 100)}),
            data_for_update,
        )
        assert response.status_code == 401


class TestCreateCategory:
    def test_success(self, admin_test_client: APIClient, built_category: models.Category):
        response = admin_test_client.post(reverse("category-list"), {"name": built_category.name})
        assert response.status_code == 201

    def test_exist_category_in_db(
            self,
            admin_test_client: APIClient,
            category: models.Category,
            built_category: models.Category
    ):
        response = admin_test_client.post(reverse("category-list"), {"name": built_category.name})
        assert response.status_code == 201

    def test_with_incorrect_data(self, admin_test_client: APIClient):
        response = admin_test_client.post(reverse("category-list"), {"field": "data"})
        assert response.status_code == 400

    def test_not_staff_user(self, user_test_client: APIClient, built_category: models.Category):
        response = user_test_client.post(reverse("category-list"), {"name": built_category.name})
        assert response.status_code == 403

    def test_not_auth_user(self, test_client: APIClient, built_category: models.Category):
        response = test_client.post(reverse("category-list"), {"name": built_category.name})
        assert response.status_code == 401


class TestCategoryRetrieve:
    def test_success(self, admin_test_client: APIClient, categories: List[models.Category]):
        category = random.choice(categories)
        response = admin_test_client.get(reverse("category-detail", args=[category.id]))
        assert response.status_code == 200
        assert response.data["id"] == category.id

    def test_with_user_client(self, user_test_client: APIClient, categories: List[models.Category]):
        category = random.choice(categories)
        response = user_test_client.get(reverse("category-detail", args=[category.id]))
        assert response.status_code == 200
        assert response.data["id"] == category.id

    def test_not_auth_client(self, test_client: APIClient, categories: List[models.Category]):
        category = random.choice(categories)
        response = test_client.get(reverse("category-detail", args=[category.id]))
        assert response.status_code == 200
        assert response.data["id"] == category.id

    def test_not_exist_category(self, admin_test_client: APIClient, categories: List[models.Category]):
        response = admin_test_client.get(reverse("category-detail", args=[len(categories) + 1]))
        assert response.status_code == 404

    def test_not_exists_any_category(self, admin_test_client: APIClient):
        response = admin_test_client.get(reverse("category-detail", args=[1]))
        assert response.status_code == 404


class TestCategoryDelete:
    def test_success(self, admin_test_client: APIClient, categories: List[models.Category]):
        category = random.choice(categories)
        response = admin_test_client.delete(reverse("category-detail", args=[category.id]))
        assert response.status_code == 204
        response = admin_test_client.get(reverse("category-detail", args=[category.id]))
        assert response.status_code == 404

    def test_with_user_client(self, user_test_client: APIClient, categories: List[models.Category]):
        category = random.choice(categories)
        response = user_test_client.delete(reverse("category-detail", args=[category.id]))
        assert response.status_code == 403

    def test_not_auth_client(self, test_client: APIClient, categories: List[models.Category]):
        category = random.choice(categories)
        response = test_client.delete(reverse("category-detail", args=[category.id]))
        assert response.status_code == 401

    def test_not_exist_category(self, admin_test_client: APIClient, categories: List[models.Category]):
        response = admin_test_client.delete(reverse("category-detail", args=[len(categories) + 1]))
        assert response.status_code == 404

    def test_not_exists_any_category(self, admin_test_client: APIClient):
        response = admin_test_client.delete(reverse("category-detail", args=[1]))
        assert response.status_code == 404


class TestCategoryUpdate:
    def test_success(self, admin_test_client: APIClient, categories: List[models.Category]):
        data_for_update = {"name": "name"}
        category = random.choice(categories)
        response = admin_test_client.put(reverse("category-detail", args=[category.id]), data_for_update)
        assert response.status_code == 200

    def test_with_invalid_data(self, admin_test_client: APIClient, categories: List[models.Category]):
        data_for_update = {"field": "value"}
        category = random.choice(categories)
        response = admin_test_client.put(reverse("category-detail", args=[category.id]), data_for_update)
        assert response.status_code == 400

    def test_with_user_client(self, user_test_client: APIClient, categories: List[models.Category]):
        data_for_update = {"name": "name"}
        category = random.choice(categories)
        response = user_test_client.put(reverse("category-detail", args=[category.id]), data_for_update)
        assert response.status_code == 403

    def test_not_auth_client(self, test_client: APIClient, categories: List[models.Category]):
        data_for_update = {"name": "name"}
        category = random.choice(categories)
        response = test_client.put(reverse("category-detail", args=[category.id]), data_for_update)
        assert response.status_code == 401

    def test_not_exist_category(self, admin_test_client: APIClient, categories: List[models.Category]):
        data_for_update = {"name": "name"}
        response = admin_test_client.put(reverse("category-detail", args=[len(categories) + 1]), data_for_update)
        assert response.status_code == 404

    def test_not_exists_any_category(self, admin_test_client: APIClient):
        data_for_update = {"name": "name"}
        response = admin_test_client.put(reverse("category-detail", args=[1]), data_for_update)
        assert response.status_code == 404


class TestCreateStatus:
    def test_success(self, admin_test_client: APIClient, built_status: models.Status):
        response = admin_test_client.post(reverse("status-list"), {"name": built_status.name})
        assert response.status_code == 201

    def test_exist_category_in_db(
            self,
            admin_test_client: APIClient,
            status: models.Status,
            built_status: models.Status
    ):
        response = admin_test_client.post(reverse("status-list"), {"name": built_status.name})
        assert response.status_code == 201

    def test_with_incorrect_data(self, admin_test_client: APIClient):
        response = admin_test_client.post(reverse("status-list"), {"field": "data"})
        assert response.status_code == 400

    def test_not_staff_user(self, user_test_client: APIClient, built_status: models.Status):
        response = user_test_client.post(reverse("status-list"), {"name": built_status.name})
        assert response.status_code == 403

    def test_not_auth_user(self, test_client: APIClient, built_status: models.Status):
        response = test_client.post(reverse("status-list"), {"name": built_status.name})
        assert response.status_code == 401


class TestStatusRetrieve:
    def test_success(self, admin_test_client: APIClient, statuses: List[models.Status]):
        status = random.choice(statuses)
        response = admin_test_client.get(reverse("status-detail", args=[status.id]))
        assert response.status_code == 200
        assert response.data["id"] == status.id

    def test_with_user_client(self, user_test_client: APIClient, statuses: List[models.Status]):
        status = random.choice(statuses)
        response = user_test_client.get(reverse("status-detail", args=[status.id]))
        assert response.status_code == 200
        assert response.data["id"] == status.id

    def test_not_auth_client(self, test_client: APIClient, statuses: List[models.Status]):
        status = random.choice(statuses)
        response = test_client.get(reverse("status-detail", args=[status.id]))
        assert response.status_code == 200
        assert response.data["id"] == status.id

    def test_not_exist_status(self, admin_test_client: APIClient, statuses: List[models.Status]):
        response = admin_test_client.get(reverse("status-detail", args=[len(statuses) + 1]))
        assert response.status_code == 404

    def test_not_exists_any_status(self, admin_test_client: APIClient):
        response = admin_test_client.get(reverse("status-detail", args=[1]))
        assert response.status_code == 404


class TestStatusDelete:
    def test_success(self, admin_test_client: APIClient, statuses: List[models.Status]):
        status = random.choice(statuses)
        response = admin_test_client.delete(reverse("status-detail", args=[status.id]))
        assert response.status_code == 204
        response = admin_test_client.get(reverse("status-detail", args=[status.id]))
        assert response.status_code == 404

    def test_with_user_client(self, user_test_client: APIClient, statuses: List[models.Status]):
        status = random.choice(statuses)
        response = user_test_client.delete(reverse("status-detail", args=[status.id]))
        assert response.status_code == 403

    def test_not_auth_client(self, test_client: APIClient, statuses: List[models.Status]):
        status = random.choice(statuses)
        response = test_client.delete(reverse("status-detail", args=[status.id]))
        assert response.status_code == 401

    def test_not_exist_status(self, admin_test_client: APIClient, statuses: List[models.Status]):
        response = admin_test_client.delete(reverse("status-detail", args=[len(statuses) + 1]))
        assert response.status_code == 404

    def test_not_exists_any_status(self, admin_test_client: APIClient):
        response = admin_test_client.delete(reverse("status-detail", args=[1]))
        assert response.status_code == 404


class TestStatusUpdate:
    def test_success(self, admin_test_client: APIClient, statuses: List[models.Status]):
        data_for_update = {"name": "name"}
        status = random.choice(statuses)
        response = admin_test_client.put(reverse("status-detail", args=[status.id]), data_for_update)
        assert response.status_code == 200

    def test_with_invalid_data(self, admin_test_client: APIClient, statuses: List[models.Status]):
        data_for_update = {"field": "value"}
        status = random.choice(statuses)
        response = admin_test_client.put(reverse("status-detail", args=[status.id]), data_for_update)
        assert response.status_code == 400

    def test_with_user_client(self, user_test_client: APIClient, statuses: List[models.Status]):
        data_for_update = {"name": "name"}
        status = random.choice(statuses)
        response = user_test_client.put(reverse("status-detail", args=[status.id]), data_for_update)
        assert response.status_code == 403

    def test_not_auth_client(self, test_client: APIClient, statuses: List[models.Status]):
        data_for_update = {"name": "name"}
        status = random.choice(statuses)
        response = test_client.put(reverse("status-detail", args=[status.id]), data_for_update)
        assert response.status_code == 401

    def test_not_exist_status(self, admin_test_client: APIClient, statuses: List[models.Status]):
        data_for_update = {"name": "name"}
        response = admin_test_client.put(reverse("status-detail", args=[len(statuses) + 1]), data_for_update)
        assert response.status_code == 404

    def test_not_exists_any_status(self, admin_test_client: APIClient):
        data_for_update = {"name": "name"}
        response = admin_test_client.put(reverse("status-detail", args=[1]), data_for_update)
        assert response.status_code == 404


class TestCreateTaskImage:
    def test_success(
            self, admin_test_client: APIClient,
            task: models.Task,
            built_task_image: models.TaskImage
    ):
        data_for_create = {k: v for k, v in model_to_dict(built_task_image).items() if v is not None}
        data_for_create["task"] = task.id
        response = admin_test_client.post(reverse("task_image-create"), data_for_create)
        response_data = response.data
        assert response_data
        assert response_data["id"]

    def test_unsuccessful(self, admin_test_client: APIClient, task: models.Task, built_task_image: models.TaskImage):
        data_for_create = {k: v for k, v in model_to_dict(built_task_image).items() if v is not None}
        data_for_create["task"] = task.id
        data_for_create["title"] = "a" * 300
        response = admin_test_client.post(reverse("task_image-create"), data_for_create)
        assert response.status_code == 400

    def test_not_exists_related_id(self, admin_test_client: APIClient, built_task_image: models.TaskImage):
        data_for_create = {k: v for k, v in model_to_dict(built_task_image).items() if v is not None}
        data_for_create["task"] = 20
        response = admin_test_client.post(reverse("task_image-create"), data_for_create)
        assert response.status_code == 400

    def test_not_task_author(self, user_test_client: APIClient, task: models.Task, built_task_image: models.TaskImage):
        data_for_create = {k: v for k, v in model_to_dict(built_task_image).items() if v is not None}
        data_for_create["task"] = task.id
        response = user_test_client.post(reverse("task_image-create"), data_for_create)
        assert response.status_code == 403

    def test_not_auth_user(self, test_client: APIClient, task: models.Task, built_task_image: models.TaskImage):
        data_for_create = {k: v for k, v in model_to_dict(built_task_image).items() if v is not None}
        data_for_create["task"] = task.id
        response = test_client.post(reverse("task_image-create"), data_for_create)
        assert response.status_code == 401


class TestRetrieveTaskImage:
    def test_success(self, admin_test_client: APIClient, task_images: List[models.TaskImage]):
        task_image = random.choice(task_images)
        response = admin_test_client.get(reverse("task_image-retrieve", args=[task_image.id]))
        response_data = response.data
        task_image_data = model_to_dict(task_image)
        assert response.status_code == 200
        assert (task_image_data["id"], task_image_data["title"]) == (response_data["id"], response_data["title"])

    def test_not_exists(self, admin_test_client: APIClient, task_images: List[models.TaskImage]):
        response = admin_test_client.get(reverse("task_image-retrieve", args=[random.randint(100, 200)]))
        assert response.status_code == 404

    def test_not_any_exist(self, admin_test_client: APIClient):
        response = admin_test_client.get(reverse("task_image-retrieve", args=[1]))
        assert response.status_code == 404

    def test_not_task_author(self, user_test_client: APIClient, task_images: List[models.TaskImage]):
        task_image = random.choice(task_images)
        response = user_test_client.get(reverse("task_image-retrieve", args=[task_image.id]))
        response_data = response.data
        task_image_data = model_to_dict(task_image)
        assert response.status_code == 200
        assert (task_image_data["id"], task_image_data["title"]) == (response_data["id"], response_data["title"])

    def test_not_auth_user(self, test_client: APIClient, task_images: List[models.TaskImage]):
        task_image = random.choice(task_images)
        response = test_client.get(reverse("task_image-retrieve", args=[task_image.id]))
        response_data = response.data
        task_image_data = model_to_dict(task_image)
        assert response.status_code == 200
        assert (task_image_data["id"], task_image_data["title"]) == (response_data["id"], response_data["title"])