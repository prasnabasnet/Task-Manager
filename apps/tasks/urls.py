from django.urls import path
from . import views
from .views.task_views import TaskListCreateView, TaskDetailView

urlpatterns = [
    path('', TaskListCreateView.as_view(), name='task-list'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
] 