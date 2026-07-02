from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.projects.models import Project

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
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
        return {
            'id': obj.owner.id,
            'email': obj.owner.email,
            'role': obj.owner.role,
        }

    def get_member_count(self, obj):
        return getattr(obj, 'member_count', obj.members.count())

    def get_task_count(self, obj):
        return getattr(obj, 'task_count', 0)