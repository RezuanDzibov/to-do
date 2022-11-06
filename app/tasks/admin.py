from django.contrib import admin
from django.contrib.admin import register
from django.contrib.admin.widgets import AdminFileWidget
from django.db import models
from django.utils.safestring import mark_safe

from .models import Category, Status, TaskImage, Task, TaskCompletion


class TaskImageWidget(AdminFileWidget):

    def render(self, name, value, attrs=None, renderer=None):
        output = []

        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)

            output.append(
                f'<a href="{image_url}" target="_blank">'
                f'<img src="{image_url}" alt="{file_name}" width="300" height="300" '
                f'style="object-fit: cover;"/> </a>')

        output.append(super(AdminFileWidget, self).render(name, value, attrs, renderer))
        return mark_safe(u"".join(output))


@register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@register(Status)
class StatusAdmin(admin.ModelAdmin):
    pass


class TaskImageInline(admin.StackedInline):
    model = TaskImage
    formfield_overrides = {
        models.ImageField: {"widget": TaskImageWidget}
    }


@register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "category", "status")
    list_filter = ("available", "category", "status")
    list_display_links = ("title", "user", "category", "status")
    inlines = [TaskImageInline]


@register(TaskCompletion)
class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "task", "user")
    list_display_links = ("__str__", "task", "user")
