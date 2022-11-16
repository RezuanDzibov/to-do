from django.urls import path
from rest_framework.routers import DefaultRouter

from tasks import views

router = DefaultRouter()
router.register("categories", views.CategoryViewSet, basename="category")
router.register("statuses", views.StatusViewSet, basename="status")

urlpatterns = [
    path("list/", views.TaskList.as_view(), name="task-list"),
    path("create/", views.CreateTask.as_view(), name="task-create"),
    path("<int:task_id>/", views.TaskRetrieve.as_view(), name="task-retrieve"),
    path("delete/<int:task_id>/", views.TaskDelete.as_view(), name="task-delete"),
    path("update/<int:task_id>/", views.TaskUpdate.as_view(), name="task-update")
]

urlpatterns += router.urls
