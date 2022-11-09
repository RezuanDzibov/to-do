from django.urls import path

from tasks import views

urlpatterns = [
    path("", views.CreateTask.as_view(), name="task-create"),
]
