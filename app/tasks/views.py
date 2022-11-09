from drf_yasg.utils import swagger_auto_schema
from rest_framework import views, status
from rest_framework.request import HttpRequest
from rest_framework.response import Response

from common.permissions import IsActive
from tasks import serializers, services


class CreateTask(views.APIView):
    permission_classes = [IsActive]

    @swagger_auto_schema(responses={200: serializers.TaskCreateSerializerOut()})
    def post(self, request: HttpRequest) -> Response:
        task = services.create_task(user=request.user, data=request.data.copy())
        return Response(data=serializers.TaskCreateSerializerOut(task).data, status=status.HTTP_201_CREATED)
