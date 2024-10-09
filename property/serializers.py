from rest_framework import serializers
from .models import Property,Favorite,PropertyImage,PropertyVideo,Transaction


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
            'year_built',
            'address',
            'city',
            'state',
            'postal_code',
            'country',
            'latitude',
            'longitude',
            'image_paths',
            'video_paths',
            'date_listed',
            'last_updated',
            'kitchen',
            'floors',
            'storage',
            'parking',
        ]
        # set to read_only so can be consumed in get requests only
        read_only_fields = ['user']
    

class FavoriteSerializer(serializers.ModelSerializer):
    
    # property=PropertySerializer()
    class Meta:
        model = Favorite
        fields = ['id', 'property', 'created_at']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.method == 'GET':
            ret['property'] = PropertySerializer(instance.property).data
        return ret


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'property', 'image']

        
class PropertyVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyVideo
        fields = ['id', 'video']
class TransactionSerializer(serializers.ModelSerializer):
    property_type = serializers.CharField(source='property.property_type', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id',
            'property',
            'property_type',
            'transaction_type',
            'seller_name',
            'buyer',
            'buyer_name',
            'date',
            'amount',
        ]
