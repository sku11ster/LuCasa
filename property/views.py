from rest_framework import viewsets ,permissions,serializers,status
from rest_framework.response import Response
from .models import Property,Favorite,PropertyImage,PropertyVideo
from .serializers import PropertySerializer,FavoriteSerializer,PropertyImageSerializer,PropertyVideoSerializer
from .permissions import IsPropertyOwner
from rest_framework import generics
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import F, ExpressionWrapper, FloatField
from rest_framework.exceptions import NotFound
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

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

class PropertySuggestionsView(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')
        if not query:
            return JsonResponse([], safe=False)
        suggestions = Property.objects.filter(title__icontains=query).values('id','title')[:10]
        return Response(suggestions)

class PropertyImageViewSet(viewsets.ViewSet):
    serializer_class = PropertyImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, property_id=None):
        try:
            property_instance = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({"detail": "Property does not exist."}, status=status.HTTP_404_NOT_FOUND)

        images = PropertyImage.objects.filter(property=property_instance)
        serializer = PropertyImageSerializer(images, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def create(self, request, property_id=None):
        serializer = PropertyImageSerializer(data=request.data)
        try:
            property_instance = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({"detail": "Property does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if property_instance.user != request.user:
            return Response({"detail": "You do not own this property."}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save(property=property_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, property_id=None):
        try:
            image_instance = PropertyImage.objects.get(id=pk, property_id=property_id)
        except PropertyImage.DoesNotExist:
            return Response({"detail": "Image not found."}, status=status.HTTP_404_NOT_FOUND)

        if image_instance.property.user != request.user:
            return Response({"detail": "You do not own this property."}, status=status.HTTP_403_FORBIDDEN)
        image_instance.image.delete(save=False)
        image_instance.delete()
        return Response({"detail": "Image deleted."}, status=status.HTTP_200_OK)

    def update(self, request, pk=None, property_id=None):
        try:
            image_instance = PropertyImage.objects.get(id=pk, property_id=property_id)
        except PropertyImage.DoesNotExist:
            return Response({"detail": "Image not found."}, status=status.HTTP_404_NOT_FOUND)

        if image_instance.property.user != request.user:
            return Response({"detail": "You do not own this property."}, status=status.HTTP_403_FORBIDDEN)

        image_instance.image.delete(save=False)

        serializer = PropertyImageSerializer(image_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PropertyVideoViewSet(viewsets.ViewSet):
    serializer_class = PropertyVideoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, property_id=None):
        try:
            property_instance = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({"detail": "Property does not exist."}, status=status.HTTP_404_NOT_FOUND)

        videos = PropertyVideo.objects.filter(property=property_instance)
        serializer = PropertyVideoSerializer(videos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request, property_id=None):
        serializer = PropertyVideoSerializer(data=request.data)
        try:
            property_instance = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({"detail": "Property does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if property_instance.user != request.user:
            return Response({"detail": "You do not own this property."}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save(property=property_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, property_id=None):
        try:
            video_instance = PropertyVideo.objects.get(id=pk, property_id=property_id)
        except PropertyVideo.DoesNotExist:
            return Response({"detail": "Video not found."}, status=status.HTTP_404_NOT_FOUND)

        if video_instance.property.user != request.user:
            return Response({"detail": "You do not own this property."}, status=status.HTTP_403_FORBIDDEN)

        video_instance.video.delete(save=False)

        video_instance.delete()
        return Response({"detail": "Video deleted."}, status=status.HTTP_200_OK)

    def update(self, request, pk=None, property_id=None):
        try:
            video_instance = PropertyVideo.objects.get(id=pk, property_id=property_id)
        except PropertyVideo.DoesNotExist:
            return Response({"detail": "Video not found."}, status=status.HTTP_404_NOT_FOUND)

        if video_instance.property.user != request.user:
            return Response({"detail": "You do not own this property."}, status=status.HTTP_403_FORBIDDEN)

        video_instance.video.delete(save=False)
        
        serializer = PropertyVideoSerializer(video_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
