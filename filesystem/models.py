from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    is_operation = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    is_login_activated = models.BooleanField(default=False)
    
class Files(models.Model):
    file = models.FileField(upload_to = 'media', blank=True,null=True)
    