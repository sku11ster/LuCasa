from django.db import models
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
import uuid
import os

User = get_user_model()

class Property(models.Model):
    PROPERTY_TYPES = (
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('condo', 'Condo'),
        ('land', 'Land'),
        ('commercial', 'Commercial'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = [
        ('for_sale', 'For Sale'),
        ('for_rent', 'For Rent'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    garage = models.PositiveIntegerField(null=True, blank=True)
    square_feet = models.IntegerField()
    lot_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    year_built = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    date_listed = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    image_paths = models.TextField(blank=True, null=True)
    video_paths = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"


def unique_image_path(instance, filename):
    ext = filename.split('.')[-1]
    unique_name = f"{uuid.uuid4().hex[:6]}_{instance.id}.{ext}"
    return os.path.join('property_images/', unique_name)

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_photos/')

    def __str__(self):
        return f"{self.property.title} Image"
    class Meta:
        ordering = ['id']
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.image.name.endswith(f"{self.id}"):
            old_image_name = self.image.name
            self.image.name = unique_image_path(self, self.image.name)
            super().save(update_fields=['image'])
                
            if default_storage.exists(old_image_name):
                default_storage.delete(old_image_name)

    
class PropertyVideo(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='property_videos/')

    def __str__(self):
        return f"{self.property.title} Video"
    class Meta:
        ordering = ['id'] 
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.video.name.endswith(f"{self.id}"):
            old_video_name = self.video.name
            self.video.name = unique_image_path(self, self.video.name)
            super().save(update_fields=['video'])
                
            if default_storage.exists(old_video_name):
                default_storage.delete(old_video_name)

class Favorite(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    property = models.ForeignKey(Property,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=('user','property')