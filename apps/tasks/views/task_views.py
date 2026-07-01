from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from apps.tasks.models.task import Task
from apps.tasks.serializers.task import TaskSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Task.objects.filter(project__members=self.request.user)
        
        project_id = self.request.query_params.get('project')
        status = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        assignee = self.request.query_params.get('assignee')

        if project_id:
            qs = qs.filter(project_id=project_id)
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        if assignee:
            qs = qs.filter(assignee_id=assignee)

        return qs.distinct()
 
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]