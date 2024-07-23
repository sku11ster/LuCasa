from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('buyer','BUYER'),
        ('seller',"SELLER"),
    )
    user_type = models.CharField(max_length=10,choices=USER_TYPE_CHOICES)
    is_individual = models.BooleanField(default=True)
    company_name = models.CharField(max_length=255,blank=True,null=True)
    contact = models.CharField(max_length=15)
    profile_picture =models.ImageField(upload_to='profile_pics/',default='/profile_pics/default.png')
    profile_banner =models.ImageField(upload_to='profile_banner/',default='/profile_banner/default.png')
    address = models.TextField(blank=True,null=True)
    website = models.TextField(blank=True,null=True)
    bio = models.TextField(blank=True,null=True)
    social_links = models.JSONField(blank=True,null=True)

    def __str__(self):
        return self.username

