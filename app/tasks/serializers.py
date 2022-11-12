from rest_framework import serializers

from tasks import models


class TaskCreateSerializerIn(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = ["title", "category", "status", "text", "available"]


class TaskCreateSerializerOut(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name")
    status = serializers.CharField(source="status.name")

    class Meta:
        model = models.Task
        fields = ["id", "category", "status", "user", "text", "available", "created_at"]


class TaskRetrieveSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name")
    status = serializers.CharField(source="status.name")

    class Meta:
        model = models.Task
        fields = ["id", "category", "status", "user", "text", "available", "created_at", "edited_at"]


class TaskListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name")
    status = serializers.CharField(source="status.name")
    user = serializers.CharField(source="user.username")

    class Meta:
        model = models.Task
        fields = ["id", "category", "status", "user", "available"]
