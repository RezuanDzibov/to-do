from django.urls import path

from tasks import views

urlpatterns = [
    path("list/", views.TaskList.as_view(), name="task-list"),
    path("create/", views.CreateTask.as_view(), name="task-create"),
    path("<int:task_id>/", views.TaskRetrieve.as_view(), name="task-retrieve"),
]
