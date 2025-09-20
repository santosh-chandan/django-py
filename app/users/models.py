from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class userProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=255, blank=True, null=True, default='')
    level = models.IntegerField(blank=True, null=True, default=0)
