from django.urls import path

from tasks import views

urlpatterns = [
    path("list/", views.TaskList.as_view(), name="task-list"),
    path("create/", views.CreateTask.as_view(), name="task-create"),
    path("<int:task_id>/", views.TaskRetrieve.as_view(), name="task-retrieve"),
    path("delete/<int:task_id>/", views.TaskDelete.as_view(), name="task-delete"),
    path("update/<int:task_id>/", views.TaskUpdate.as_view(), name="task-update")
]
