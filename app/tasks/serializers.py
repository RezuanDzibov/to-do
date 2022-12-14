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


class TaskListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name")
    status = serializers.CharField(source="status.name")
    user = serializers.CharField(source="user.username")

    class Meta:
        model = models.Task
        fields = ["id", "category", "status", "user", "available"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ["id", "name"]


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ["id", "name"]


class TaskImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TaskImage
        fields = ["title", "image", "task"]


class TaskImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TaskImage
        fields = ["id", "title", "image"]


class TaskRetrieveSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name")
    status = serializers.CharField(source="status.name")
    images = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name="task_image-retrieve")

    class Meta:
        model = models.Task
        fields = [
            "id",
            "title",
            "category",
            "status",
            "user",
            "text",
            "available",
            "created_at",
            "edited_at",
            "images",
        ]
