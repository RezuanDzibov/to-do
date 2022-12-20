from django.db import models

from common.models import Image
from user.models import User


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


class Status(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Task Status"
        verbose_name_plural = "Task Statuses"

    def __str__(self) -> str:
        return self.name


class TaskImage(Image):
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey("Task", on_delete=models.CASCADE, related_name="images")

    class Meta:
        verbose_name = "Task Image"
        verbose_name_plural = "Task Images"

    def __str__(self) -> str:
        return f"{self.task.id} task's {self.title}"


class Task(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    status = models.ForeignKey(Status, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self) -> str:
        return self.title[:30]


class TaskCompletion(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Task Completion"
        verbose_name_plural = "Task Completions"

    def __str__(self) -> str:
        return f"{self.task.title[:20]} by {self.user.first_name} {self.user.last_name}"
