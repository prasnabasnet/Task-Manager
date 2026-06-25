from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Project, ProjectMember

User = get_user_model()


class ProjectMemberSerializer(serializers.ModelSerializer):
    """Serializer for displaying project member details."""

    user_id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = ProjectMember
        fields = ['user_id', 'email', 'role', 'joined_at']


class AddMemberSerializer(serializers.Serializer):
    """Serializer for adding a member to a project."""

    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        """Validate that the user exists."""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError('User not found.')
        return value


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for listing and creating projects."""

    owner = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'description',
            'owner',
            'member_count',
            'task_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def get_owner(self, obj):
        """Return basic owner details."""
        return {
            'id': obj.owner.id,
            'email': obj.owner.email,
            'role': obj.owner.role,
        }

    def get_member_count(self, obj):
        """Return total number of project members."""
        return obj.members.count()

    def get_task_count(self, obj):
        """Return total number of tasks in the project."""
        return obj.tasks.count() if hasattr(obj, 'tasks') else 0