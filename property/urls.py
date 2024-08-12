from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet,PropertySearchView,FavoriteView,PropertySuggestionsView,PropertyImageCreateView,PropertyVideoCreateView,PropertyImageDeleteView,PropertyVideoDeleteView
from django.urls import path,include

router = DefaultRouter()
router.register(r'property', PropertyViewSet)
router.register(r'favorites', FavoriteView)

urlpatterns = [
    path('', include(router.urls)),
    path('search/', PropertySearchView.as_view(), name='property-search'),
    path('suggestions/', PropertySuggestionsView.as_view(), name='property_suggestions'),
    path('property/<int:property_id>/images/add/', PropertyImageCreateView.as_view(), name='property-image-add'),
    path('property/<int:property_id>/videos/add/', PropertyVideoCreateView.as_view(), name='property-video-add'),
    path('property/<int:property_id>/images/<str:image_name>/delete/', PropertyImageDeleteView.as_view(), name='property-image-delete'),
    path('property/<int:property_id>/images/<str:image_name>/delete/', PropertyVideoDeleteView.as_view(), name='property-image-delete'),

]
