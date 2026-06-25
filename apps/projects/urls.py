from django.urls import path

from .views import (
    ProjectDetailView,
    ProjectListCreateView,
    ProjectMemberListAddView,
    ProjectMemberRemoveView,
)

urlpatterns = [
    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('projects/<int:pk>/members/', ProjectMemberListAddView.as_view(), name='project-members'),
    path('projects/<int:pk>/members/<int:uid>/', ProjectMemberRemoveView.as_view(), name='project-member-remove'),
]