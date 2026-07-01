from django.urls import path
from .views import CommentViewSet

urlpatterns = [
    # example: GET /api/comments/?target_type=project&target_id=1
    path('comments/', CommentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='comment-list'),
    
    # Managing individual comments
    path('comments/<int:pk>/', CommentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='comment-detail'),
]