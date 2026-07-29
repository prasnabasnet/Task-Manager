from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer
from apps.common.services import BaseService

class CreateTaskService(BaseService):

    def validate(self) -> None:
        project = self.validated_data.get('project')
        is_member = (
            getattr(self.user, 'is_admin', False) 
            or project.owwner == self.user
            or project.members.filter(id=self.user.id).exists()
        )
        self.check_permission(is_member, "You do not have permission to create a task in this project.")

    def process(self) -> Task:
        assignees = self.validated_data.pop('assignees', [])
        task = Task.objects.create(created_by=self.user, **self.validated_data)

        if assignees:
            task.assignees.set(assignees)

        self.log_info(f"Task '{task.title}' created by user '{self.user.username}' in project '{task.project.name}'.")

        self._broadcast_websocket_event(task, action="created")

        return task

    def _broadcast_websocket_event(self, task: Task, action: str) -> None:
        channel_layer = get_channel_layer()
        group_name = f"project_{task.project.id}_tasks"
        serialized_data = TaskSerializer(task).data

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "task_event",
                "action": action,
                "task": serialized_data,
            }
        )

class UpdateTaskService(BaseService):

    def process(self)-> Task:
        assignees = self.validated_data.pop('assignees', None)
        old_status = self.task.status
        old_priority = self.task.priority

        for attr, value in self.validated_data.items():
            setattr(self.task, attr, value)
        self.task.save()

        if assignees is not None:
            self.task.assignees.set(assignees)

        status_changed = old_status != self.task.status
        priority_changed = old_priority != self.task.priority

        self.log_info(
            f"Task '{self.task.title}' updated by user '{self.user.username}' in project '{self.task.project.name}'. "
            f"Status changed: {status_changed}, Priority changed: {priority_changed}."
        )

        self._broadcast_websocket_event(
            task=self.task, action="updated", status_changed=status_changed, priority_changed=priority_changed
            )

        return self.task

    def _broadcast_websocket_event(self, task: Task, action: str, **kwargs) -> None:
        channel_layer = get_channel_layer()
        group_name = f"project_{task.project.id}_tasks"
        serialized_data = TaskSerializer(task).data

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "task_event",
                "action": action,
                "task": serialized_data,
                "status_changed": kwargs.get("status_changed", False),
                "priority_changed": kwargs.get("priority_changed", False),
            }
        )

class DeleteTaskService(BaseService):

    def process(self) -> None:
        project_id = self.task.project_id
        project_name = self.task.project.name
        task_id = self.task.id

        self.task.delete()
        self.log_info(f"Task '{task_id}' deleted by user '{self.user.username}' from project '{project_name}' (ID: {project_id}).")

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"project_{project_id}_tasks",
            {
                "type": "task_event",
                "action": "deleted",
                "task_id": task_id,
            },
        )



        