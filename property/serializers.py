from rest_framework import serializers
from .models import Property,Favorite,PropertyImage,PropertyVideo

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
            'image_paths',
            'video_paths'
        ]
        # set to read_only so can be consumed in get requests only
        read_only_fields = ['user']
    

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'property', 'created_at']



class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image']


class PropertyVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyVideo
        fields = ['id', 'video']