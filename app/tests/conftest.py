from functools import partial
from random import randint
from typing import List

import faker
import pytest

from _pytest.fixtures import SubRequest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from config import settings
from tasks import models
from tests import factories


User = get_user_model()


@pytest.fixture(scope="function")
def admin_user_data() -> dict:
    data = {
        "username": settings.ADMIN_FIXTURE_USERNAME,
        "email": settings.ADMIN_FIXTURE_EMAIL,
        "password": settings.ADMIN_FIXTURE_PASSWORD,
        "first_name": settings.ADMIN_FIXTURE_FIRST_NAME,
        "last_name": settings.ADMIN_FIXTURE_LAST_NAME,
    }
    return data


@pytest.fixture(scope="function")
def category(db) -> models.Category:
    category = factories.CategoryFactory.create()
    return category


@pytest.fixture(scope="function")
def status(db) -> models.Status:
    status = factories.StatusFactory.create()
    return status


@pytest.fixture(scope="function")
def admin_user(db, admin_user_data: dict) -> User:
    user = User.objects.create_superuser(**admin_user_data)
    return user


@pytest.fixture(scope="function")
def built_task(category: models.Category, status: models.Status) -> models.Task:
    task = factories.TaskFactory.build(category=category, status=status)
    return task


@pytest.fixture(scope="function")
def auth_test_client(admin_user: User) -> APIClient:
    url = reverse("jwt-create")
    data = {"username": admin_user.username, "password": settings.ADMIN_FIXTURE_PASSWORD}
    response = APIClient().post(url, data)
    access_token = response.data["access"]
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="JWT " + access_token)
    return client


@pytest.fixture(scope="function")
def test_client() -> APIClient:
    return APIClient()


@pytest.fixture(scope="function")
def task(request: SubRequest, admin_user: User, built_task: models.Task) -> models.Task:
    if hasattr(request, "param"):
        for key, value in request.param.items():
            setattr(built_task, key, value)
    built_task.user = admin_user
    built_task.save()
    return built_task


@pytest.fixture(scope="function")
def tasks(request: SubRequest, admin_user: User, category: models.Category, status: models.Status) -> List[models.Task]:
    fun = partial(factories.TaskFactory.build_batch, user=admin_user, category=category, status=status)
    if hasattr(request, "param") and request.param is int and request.param > 0:
        tasks = fun(request.param)
    else:
        tasks = fun(randint(1, 10))
    for task in tasks:
        task.available = faker.Faker().pybool()
    models.Task.objects.bulk_create(tasks)
    return tasks

