from rest_framework import serializers
from .models import Property,Favorite

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
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

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        return Property.objects.create(user=user, **validated_data)
    

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'property', 'created_at']
