from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet,PropertySearchView
from django.urls import path,include

router = DefaultRouter()
router.register(r'property', PropertyViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('search/', PropertySearchView.as_view(), name='property-search'),


]
