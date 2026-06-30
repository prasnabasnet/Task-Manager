from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.projects.views import ProjectMemberListAddView, ProjectMemberRemoveView, ProjectViewSet

router = DefaultRouter()
router.register('projects', ProjectViewSet, basename='project')

urlpatterns = [
    path('', include(router.urls)),
    path('projects/<int:pk>/members/', ProjectMemberListAddView.as_view(), name='project-members'),
    path('projects/<int:pk>/members/<int:uid>/', ProjectMemberRemoveView.as_view(), name='project-member-remove'),
]