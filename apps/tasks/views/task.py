from django.shortcuts import render
from apps.tasks.models.task import Task
from apps.tasks.serializers.task import TaskSerializer
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from apps.tasks.filters import TaskFilter


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter


    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user).order_by('-due_date')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


