from django.urls import path
from .views import CommentViewSet

urlpatterns = [
    path('projects/<int:pid>/tasks/<int:tid>/comments/', CommentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='comment-list'),
    
    path('projects/<int:pid>/tasks/<int:tid>/comments/<int:pk>/', CommentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='comment-detail'),
]