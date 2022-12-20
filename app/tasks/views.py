from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import views, status, permissions, generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import HttpRequest, Request
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
        serializer_context = {
            "request": request,
        }
        if not task.available:
            if not request.user or request.user.id != task.user.id:
                raise PermissionDenied(code=403, detail="You aren't allowed")
        return Response(data=serializers.TaskRetrieveSerializer(task, context=serializer_context).data, status=status.HTTP_200_OK)


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
    http_method_names = ["get", "post", "head", "put", "delete"]


class StatusViewSet(ModelViewSet):
    queryset = models.Status.objects.all()
    filter_backends = (DjangoFilterBackend,)
    serializer_class = serializers.StatusSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsStaffOrReadOnly]
    http_method_names = ["get", "post", "head", "put", "delete"]


class TaskImageCreate(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={201: serializers.TaskImageSerializer()})
    def post(self, request: HttpRequest):
        data = request.data.copy().dict() | request.FILES.copy().dict()
        task_image = services.create_task_image(user=request.user, data=data)
        return Response(data=serializers.TaskImageSerializer(task_image).data, status=status.HTTP_201_CREATED)


class TaskImageRetrieve(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={201: serializers.TaskImageSerializer()})
    def get(self, request: HttpRequest, pk: int):
        task_image = services.get_task_image(task_image_id=pk)
        return Response(data=serializers.TaskImageSerializer(task_image).data, status=status.HTTP_200_OK)
