from drf_yasg.utils import swagger_auto_schema
from rest_framework import views, status, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import HttpRequest
from rest_framework.response import Response
from rest_framework import exceptions

from common.permissions import IsActive
from tasks import serializers, services


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
