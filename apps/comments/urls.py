from django.urls import path
from apps.comments.views import CommentViewSet

urlpatterns = [
    path('comments/', CommentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='comment-list'),
    
    path('comments/<int:pk>/', CommentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='comment-detail'),
]