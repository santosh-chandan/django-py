from django.db import models
from django.conf import settings

class Post(models.Model):
    '''
        When you create a ForeignKey (or OneToOneField / ManyToManyField), Django automatically creates a reverse relation so that 
        you can access related objects from the other side of the relationship.
        By default, Django names this reverse relation <modelname>_set.
        If you want a custom name instead of post_set, you use related_name.
        # without related name => user = User.objects.first() user.post_set.all()   # All posts by that user
        # with related name => user.posts.all()

        Meta is an inner class inside a Django model where you define metadata (extra options) about the model. 
        It doesn’t create a database field — it just tells Django how to treat the model
    '''
    title= models.CharField(max_length=255)
    body= models.TextField()
    user= models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
