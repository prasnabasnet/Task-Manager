from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.tasks.models import Task
from apps.users.serializers import UserDetailSerializer

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    created_by = UserDetailSerializer(read_only=True)
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "created_by",
            "due_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["assignee"] = (
            UserDetailSerializer(instance.assignee).data if instance.assignee else None
        )
        return representation
