from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    address = models.TextField(blank=True)
    about_me = models.TextField(blank=True)
    country = models.CharField(max_length=20, blank=True)
    enrolled_status = models.BooleanField(default=False)


    def __str__(self):
        return self.user.username