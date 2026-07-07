from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    mentions = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='mentioned_comments')
    
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE) # Content type tracks every model installed in the app. So it has info on all the tables.
    object_id = models.PositiveIntegerField() # Object id tracks the id of the row in the table.
    commentable_object = GenericForeignKey('content_type', 'object_id') # GenericForeignKey is a way to link to any model in the app.
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        db_table = 'comments_comment'

    def __str__(self):
        return f"Comment by {self.author} on {self.commentable_object}"
