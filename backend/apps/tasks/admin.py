from django.contrib import admin
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