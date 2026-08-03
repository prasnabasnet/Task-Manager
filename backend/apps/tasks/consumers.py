from channels.generic.websocket import AsyncJsonWebsocketConsumer


class TaskConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.group_name = f"project_{self.project_id}"
        self.tasks_group_name = f"project_{self.project_id}_tasks"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.channel_layer.group_add(self.tasks_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_discard(self.tasks_group_name, self.channel_name)

    async def task_event(self, event):
        await self.send_json({
            "action": event.get("action"),
            "task": event.get("task"),
            "task_id": event.get("task_id"),
            "status_changed": event.get("status_changed", False),
            "priority_changed": event.get("priority_changed", False),
        })