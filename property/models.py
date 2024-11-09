from django.db import models
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from ckeditor.fields import RichTextField

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
    description = RichTextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='for_sale')
    price = models.IntegerField()
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    garage = models.PositiveIntegerField()
    square_feet = models.IntegerField()
    year_built = models.IntegerField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    views = models.PositiveIntegerField(default=0)
    date_listed = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    image_paths = models.TextField(blank=True, null=True)
    video_paths = models.TextField(blank=True, null=True)
    kitchen = models.PositiveIntegerField()
    floors = models.PositiveIntegerField()
    storage = models.PositiveIntegerField()
    parking = models.PositiveIntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"
    
    def mark_as_sold(self):
        Transaction.objects.create(
            property=self,
            seller=self.user,
            transaction_type='sold',
            amount=self.price 
        )
        self.status = 'sold'
        self.save()

    def mark_as_rented(self):
        Transaction.objects.create(
            property=self,
            seller=self.user,
            transaction_type='rented',
            amount=self.price  
        )
        self.status = 'rented'
        self.save()



class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='property_images/')

class PropertyVideo(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='videos')
    video = models.ImageField(upload_to='property_videos/')

    def __str__(self):
        return f"{self.property.title} Video"

    class Meta:
        ordering = ['id']
    


class Favorite(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    property = models.ForeignKey(Property,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=('user','property')

class Transaction(models.Model):

    TRANSACTION_TYPE_CHOICES = [
        ('list', 'Listed'), 
        ('sold', 'Sold'),
        ('rented', 'Rented'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    property = models.ForeignKey(Property,on_delete=models.CASCADE)   
    transaction_type = models.CharField(max_length=10,choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.property.id} - {self.transaction_type}'
