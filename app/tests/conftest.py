import pytest
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
