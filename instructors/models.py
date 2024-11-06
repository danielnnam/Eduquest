from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    expertise = models.TextField()
    phone = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.user.username