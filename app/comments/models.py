from django.db import models
from django.contrib.auth.models import User
from app.posts.models import Post
# Create your models here.

class Comment(models.Model):
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='comments'
        )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table='post_comments'

    def __str__(self):
        return self.author.username
