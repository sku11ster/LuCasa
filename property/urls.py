from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet,PropertySearchView,FavoriteView,PropertySuggestionsView
from django.urls import path,include

router = DefaultRouter()
router.register(r'property', PropertyViewSet)
router.register(r'favorites', FavoriteView)

urlpatterns = [
    path('', include(router.urls)),
    path('search/', PropertySearchView.as_view(), name='property-search'),
     path('suggestions/', PropertySuggestionsView.as_view(), name='property_suggestions'),
]
