from rest_framework import viewsets ,permissions
from rest_framework.response import Response
from .models import Property,Favorite
from .serializers import PropertySerializer,FavoriteSerializer
from .permissions import IsPropertyOwner
from rest_framework import generics
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import F, ExpressionWrapper, FloatField
from rest_framework.exceptions import NotFound
import logging



logger = logging.getLogger("mylogger")

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        else:
            return [IsPropertyOwner()]

    def get_queryset(self):
        if self.request.method == 'GET':
            queryset = Property.objects.filter(user=self.request.user)
        else:
            queryset = Property.objects.filter(user=self.request.user)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
        
    def retrieve(self, request, *args, **kwargs):

        queryset = Property.objects.all()
        pk = kwargs.get('pk')
        try:
            property_instance = queryset.get(pk=pk)
        except Property.DoesNotExist:
            raise NotFound("Property not found.")
        
        serializer = self.get_serializer(property_instance)
        return Response(serializer.data)

#Using Trigram for cost effective apporach
class PropertySearchView(generics.ListAPIView):
    serializer_class = PropertySerializer

    def get_queryset(self):
        queryset = Property.objects.all()
        search_params = self.request.query_params

        query = search_params.get('query')
        if query:
            queryset = queryset.annotate(
                title_similarity=TrigramSimilarity('title', query),
                description_similarity=TrigramSimilarity('description', query)
            ).annotate(
                combined_similarity=ExpressionWrapper(
                    F('title_similarity') + F('description_similarity'),
                    output_field=FloatField()
                )
            ).filter(combined_similarity__gt=0.01).order_by('-combined_similarity')


        filters = {
            'user': 'user',
            'property_type': 'property_type',
            'status': 'status',
            'price__gte': 'min_price',
            'price__lte': 'max_price',
            'bedrooms__gte': 'min_bedrooms',
            'bedrooms__lte': 'max_bedrooms',
            'bathrooms__gte': 'min_bathrooms',
            'bathrooms__lte': 'max_bathrooms',
            'garage__gte': 'min_garage',
            'garage__lte': 'max_garage',
            'square_feet__gte': 'min_square_feet',
            'square_feet__lte': 'max_square_feet',
            'city__icontains': 'city',
            'state__icontains': 'state',
            'country__icontains': 'country',
        }

        for field, param in filters.items():
            value = search_params.get(param)
            if value:
                queryset = queryset.filter(**{field: value})

        return queryset
    

class FavoriteView(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Favorite.objects.all()

    def get_queryset(self):
        return Favorite.objects.filter(user = self.request.user)
    
    def perform_create(self,serializer):
        serializer.save(user=self.request.user)
