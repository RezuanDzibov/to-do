from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import views, status, permissions, generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import HttpRequest
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from common.permissions import IsActive, IsStaffOrReadOnly
from tasks import serializers, services, models
from tasks.filters import TaskFilter


class CreateTask(views.APIView):
    permission_classes = [IsActive]

    @swagger_auto_schema(responses={201: serializers.TaskCreateSerializerOut()})
    def post(self, request: HttpRequest) -> Response:
        task = services.create_task(user=request.user, data=request.data.copy())
        return Response(data=serializers.TaskCreateSerializerOut(task).data, status=status.HTTP_201_CREATED)


class TaskRetrieve(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: serializers.TaskRetrieveSerializer()})
    def get(self, request: HttpRequest, task_id: int) -> Response:
        task = services.get_task(id_=task_id)
        if not task.available:
            if not request.user or request.user.id != task.user.id:
                raise PermissionDenied(code=403, detail="You aren't allowed")
        return Response(data=serializers.TaskRetrieveSerializer(task).data, status=status.HTTP_200_OK)


class TaskList(generics.ListAPIView):
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter
    permission_classes = [permissions.AllowAny]


class TaskDelete(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: None})
    def delete(self, request: HttpRequest, task_id: int) -> Response:
        services.delete_task(user=request.user, id_=task_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskUpdate(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: serializers.TaskRetrieveSerializer()})
    def put(self, request: HttpRequest, task_id: int) -> Response:
        task = services.update_task(user=request.user, id_=task_id, data=request.data.copy().dict())
        return Response(data=serializers.TaskRetrieveSerializer(task).data, status=status.HTTP_200_OK)


class CategoryViewSet(ModelViewSet):
    queryset = models.Category.objects.all()
    filter_backends = (DjangoFilterBackend,)
    serializer_class = serializers.CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsStaffOrReadOnly]
    http_method_names = ["get", "post", "head", "put"]
