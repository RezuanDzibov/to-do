from django.urls import path

from tasks import views

urlpatterns = [
    path("", views.CreateTask.as_view(), name="task-create"),
    path("<int:task_id>/", views.TaskRetrieve.as_view(), name="task-retrieve")
]
