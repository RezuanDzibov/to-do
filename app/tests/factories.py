import factory
from faker import Faker

from tasks import models

fake = Faker()


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
