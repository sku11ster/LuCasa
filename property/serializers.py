from rest_framework import serializers
from .models import Property,Favorite

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            'id',
            'user',
            'title',
            'description',
            'property_type',
            'status',
            'price',
            'bedrooms',
            'bathrooms',
            'garage',
            'square_feet',
            'lot_size',
            'year_built',
            'address',
            'city',
            'state',
            'postal_code',
            'country',
            'latitude',
            'longitude',
            'photos',
            'videos'
        ]
        # set to read_only so can be consumed in get requests only
        read_only_fields = ['user']
    

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'property', 'created_at']
