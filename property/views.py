from rest_framework import viewsets ,permissions,serializers,status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Property,Favorite,PropertyImage,PropertyVideo
from .serializers import PropertySerializer,FavoriteSerializer,PropertyVideoSerializer,PropertyImageSerializer
from .permissions import IsPropertyOwner
from rest_framework import generics
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import F, ExpressionWrapper, FloatField
from rest_framework.exceptions import NotFound
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

import logging


logger = logging.getLogger("mylogger")

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
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


class PropertyImageCreateView(APIView):
    serializer_class = PropertyImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        property_id = self.kwargs.get('property_id')
        user = self.request.user
        serializer = self.serializer_class(data=request.data)

        try:
            property_instance = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({"detail": "Property does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        if property_instance.user != user:
            return Response({"detail": "You do not own this property."}, status=status.HTTP_403_FORBIDDEN)
        
        if serializer.is_valid():
            serializer.save(property=property_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PropertyVideoCreateView(generics.CreateAPIView):
    serializer_class = PropertyVideoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        property_id = self.kwargs.get('property_id')
        user = self.request.user
        
        try:
            property_instance = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            raise serializers.ValidationError({"detail": "Property does not exist."}, code=status.HTTP_404_NOT_FOUND)
        
        if property_instance.user != user:
            raise serializers.ValidationError({"detail": "You do not own this property."}, code=status.HTTP_403_FORBIDDEN)
        
        serializer.save(property=property_instance)
    
class PropertyImageDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, property_id, image_name, *args, **kwargs):
        user = request.user

        property_instance = get_object_or_404(Property, id=property_id)
        if property_instance.user != user:
            return Response({"detail": "You do not own this property."}, status=status.HTTP_403_FORBIDDEN)
        try:
            image_id = int(image_name.split('_')[1].split('.')[0])
        except (IndexError, ValueError) as e:
            return Response({"detail": "Invalid image name format."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            image_instance = PropertyImage.objects.get(property=property_instance, id=image_id)
        except PropertyImage.DoesNotExist:
            return Response({"detail": "Image does not exist."}, status=status.HTTP_404_NOT_FOUND)

        image_path = image_instance.image.name
        image_instance.delete()

        if default_storage.exists(image_path):
            default_storage.delete(image_path)

        return Response({"detail": "Image deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class PropertyVideoDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, property_id, video_name, *args, **kwargs):
        user = request.user

        property_instance = get_object_or_404(Property, id=property_id)

        if property_instance.user != user:
            return Response({"detail": "You do not own this property."}, status=status.HTTP_403_FORBIDDEN)

        try:
            video_id = int(video_name.split('_')[1].split('.')[0])
        except (IndexError, ValueError) as e:
            return Response({"detail": "Invalid video name format."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            video_instance = PropertyVideo.objects.get(property=property_instance, id=video_id)
        except PropertyVideo.DoesNotExist:
            return Response({"detail": "Video does not exist."}, status=status.HTTP_404_NOT_FOUND)

        video_path = video_instance.video.name
        
        video_instance.delete()

        if default_storage.exists(video_path):
            default_storage.delete(video_path)

        return Response({"detail": "Video deleted successfully."}, status=status.HTTP_204_NO_CONTENT)