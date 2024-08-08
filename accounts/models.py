# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('buyer','BUYER'),
        ('seller',"SELLER"),
    )
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    is_individual = models.BooleanField(default=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=15, blank=True, null=True)  
    address = models.TextField(blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    social_links = models.JSONField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='/profile_pics/default.png')
    profile_banner = models.ImageField(upload_to='profile_banner/', default='/profile_banner/default.png')

    def __str__(self):
        return self.username

class PasswordResetToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)
    
    def __str__(self):
        return f'{self.user} - {self.token}'