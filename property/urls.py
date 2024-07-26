from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet
from django.urls import path,include

router = DefaultRouter()
router.register(r'property', PropertyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
