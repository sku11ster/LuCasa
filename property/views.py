from rest_framework import viewsets ,permissions,serializers,status
from rest_framework.response import Response
from .models import Property,Favorite,PropertyImage,PropertyVideo,Transaction
from .serializers import PropertySerializer,FavoriteSerializer,PropertyImageSerializer,PropertyVideoSerializer,TransactionSerializer
from .permissions import IsPropertyOwner
from rest_framework import generics
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import F, ExpressionWrapper, FloatField
from rest_framework.exceptions import NotFound
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.utils.dateparse import parse_date
from django.db.models import Q
from accounts.models import CustomUser
from django.utils.timezone import now, timedelta

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


class TransactionListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        property_type = request.query_params.get('property_type')
        transaction_type = request.query_params.get('transaction_type')
        property_id = request.query_params.get('property_id')

        filters = Q(seller = request.user)

        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                filters &= Q(date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                filters &= Q(date__lte=end_date)

        if property_type:
            filters &= Q(property__property_type=property_type)

        if transaction_type:
            filters &= Q(transaction_type=transaction_type)
        
        if property_id:
            filters &= Q(property=property_id)

        queryset = Transaction.objects.filter(filters)

        serializer = TransactionSerializer(queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class MarkPropertyTransactionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, property_id, transaction_type):
        if transaction_type not in ['sold', 'rented']:
            return Response(
                {"error": "Invalid transaction type. Please use 'sold' or 'rented'."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        property = get_object_or_404(Property, id=property_id, user=request.user)

        if transaction_type == 'sold':
            if property.status == 'sold':
                return Response(
                    {"error": f"Property {property.title} is already marked as sold."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            property.mark_as_sold()
            success_message = f"Property {property.title} marked as sold."
        elif transaction_type == 'rented':
            if property.status == 'rented':
                return Response(
                    {"error": f"Property {property.title} is already marked as rented."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            property.mark_as_rented()
            success_message = f"Property {property.title} marked as rented."

        return Response({"success": success_message}, status=status.HTTP_200_OK)
    
class DashboardDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # Transactions by time
        last_24_hours = now() - timedelta(hours=24)
        last_7_days = now() - timedelta(days=7)
        last_30_days = now() - timedelta(days=30)

        transactions_24h = Transaction.objects.filter(seller=user, date__gte=last_24_hours, transaction_type='sold')
        transactions_7d = Transaction.objects.filter(seller=user, date__gte=last_7_days, transaction_type='sold')
        transactions_30d = Transaction.objects.filter(seller=user, date__gte=last_30_days, transaction_type='sold')

        transactions_data = {
            "transactions_24h": TransactionSerializer(transactions_24h, many=True).data,
            "transactions_7d": TransactionSerializer(transactions_7d, many=True).data,
            "transactions_30d": TransactionSerializer(transactions_30d, many=True).data,
        }

        # Favorite Properties
        favorites = Favorite.objects.filter(user=request.user)
        favorites_data = FavoriteSerializer(favorites, many=True).data
        
        active_status = ['for_sale','for_rent']
        
        # Active Listings
        active_listings = Property.objects.filter(user=user, status__in=active_status)
        active_listings_data = PropertySerializer(active_listings, many=True).data

        return Response({
            "transactions": transactions_data,
            "favorites": favorites_data,
            "active_listings": active_listings_data,
        })