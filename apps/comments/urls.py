from django.urls import path
from apps.comments.views import TaskCommentListCreateView, CommentDetailView

urlpatterns = [
    path('projects/<int:pid>/tasks/<int:tid>/comments/', TaskCommentListCreateView.as_view(), name='task-comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
]
