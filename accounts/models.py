from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('buyer','BUYER'),
        ('seller',"SELLER"),
    )