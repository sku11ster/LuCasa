from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path,include,re_path

router = DefaultRouter()
router.register(r'property', PropertyViewSet)
router.register(r'favorites', FavoriteView)

router.register(r'property/(?P<property_id>[^/.]+)/images', PropertyImageViewSet, basename='propertyimage')
router.register(r'property/(?P<property_id>[^/.]+)/videos', PropertyVideoViewSet, basename='propertyvideo')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', PropertySearchView.as_view(), name='property-search'),
    path('suggestions/', PropertySuggestionsView.as_view(), name='property_suggestions'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('properties/<int:property_id>/transaction/<str:transaction_type>/', MarkPropertyTransactionView.as_view(), name='mark-property-transaction'),
    path('dashboard/', DashboardDataView.as_view(), name='dashboard-data'),



]
