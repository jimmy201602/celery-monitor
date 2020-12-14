from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class ActionLog(models.Model):
    user = models.ForeignKey(User, to_field='username')
    action = models.CharField(max_length=30, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    detail = models.TextField(blank=True)
