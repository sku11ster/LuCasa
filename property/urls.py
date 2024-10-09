from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path,include,re_path

router = DefaultRouter()
router.register(r'property', PropertyViewSet)
router.register(r'favorites', FavoriteView)

# router.register(r'property/(?P<property_id>[^/.]+)/images', PropertyImageViewSet, basename='propertyimage')
router.register(r'property/(?P<property_id>[^/.]+)/videos', PropertyVideoViewSet, basename='propertyvideo')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', PropertySearchView.as_view(), name='property-search'),
    path('suggestions/', PropertySuggestionsView.as_view(), name='property_suggestions'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('properties/<int:property_id>/transaction/<str:transaction_type>/', MarkPropertyTransactionView.as_view(), name='mark-property-transaction'),
    path('dashboard/', DashboardDataView.as_view(), name='dashboard-data'),
    path('property/<int:property_id>/images/', PropertyImageViewSet.as_view({
        'get': 'list',        # List all images for a specific property
        'post': 'create',     # Upload a new image for a specific property
    })),
    path('property/<int:property_id>/images/<int:pk>/', PropertyImageViewSet.as_view({
        'get': 'retrieve',    # Retrieve a specific image
        'put': 'update',      # Update a specific image
        'patch': 'partial_update',  # Partial update of an image
        'delete': 'destroy',  # Delete a specific image
    })),


]
