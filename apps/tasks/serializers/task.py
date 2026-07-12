from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.tasks.models import Task
from apps.users.serializers import UserDetailSerializer

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    created_by = UserDetailSerializer(read_only=True)
    assignee = UserDetailSerializer(read_only=True)
    assignee_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
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
            "assignee_id",
            "created_by",
            "due_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def validate_assignee_id(self, value):
        if value is None:
            return value
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Assignee not found.")
        return value

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)
