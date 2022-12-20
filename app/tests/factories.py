import factory
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils.text import slugify
from faker import Faker

from tasks import models

fake = Faker()
User = get_user_model()


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Category

    name = factory.LazyAttribute(lambda obj: fake.color_name())


class StatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Status

    name = factory.LazyAttribute(lambda obj: fake.color_name())


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Task

    title = factory.LazyAttribute(lambda obj: fake.color_name())
    text = factory.LazyAttribute(lambda obj: fake.text())
    available = factory.LazyAttribute(lambda obj: fake.pybool())


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyAttribute(lambda obj: slugify(fake.color_name()))
    first_name = factory.LazyAttribute(lambda obj: fake.first_name())
    last_name = factory.LazyAttribute(lambda obj: fake.last_name())
    email = factory.LazyAttribute(lambda obj: fake.email())
    is_staff = False
    is_active = True
    password = factory.LazyAttribute(lambda obj: fake.password())


class TaskImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TaskImage
    title = factory.LazyAttribute(lambda obj: fake.color_name())
    image = factory.LazyAttribute(
        lambda _: ContentFile(
            factory.django.ImageField()._make_data(
                {"width": 1024, "height": 768}
            ), "example.jpg"
        )
    )
