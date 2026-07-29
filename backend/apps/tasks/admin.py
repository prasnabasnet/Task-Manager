from django.contrib import admin

from unfold.admin import ModelAdmin
from unfold.decorators import display
from apps.tasks.models import Task  


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    #  The columns displayed on the Task list page
    list_display = ('title', 'project', 'status', 'priority', 'display_assignees', 'due_date', 'created_at')
    
    # Sidebar filters on the right-hand side
    list_filter = ('status', 'priority', 'project', 'due_date')
    
    #  Top search bar fields
    search_fields = ('title', 'description', 'assignees__email', 'created_by__email')
    
    # Default sorting order in the admin panel
    ordering = ('-created_at',)
    
    # Fields that are read-only inside the Task detail editor
    readonly_fields = ('created_at', 'updated_at')

    def display_assignees(self, obj):
        return ", ".join([user.email for user in obj.assignees.all()])
    display_assignees.short_description = 'Assignees'
    @display(description="Status",
             ordering="status",
             label={
                 Task.Status.TODO: "danger",
                 Task.Status.IN_PROGRESS: "warning",
                 Task.Status.DONE: "success",
             },
             )

    def display_status(self, obj):
        return obj.get_status_display()

    @display(description="Priority",
             ordering="priority",
             label={
                 Task.Priority.LOW: "info",
                 Task.Priority.MEDIUM: "primary",
                 Task.Priority.HIGH: "danger",
             },
                )
    def display_priority(self, obj):
        return obj.get_priority_display()
