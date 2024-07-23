from django.urls import path
from .views import LucasaRegisterView

urlpatterns = [
     path('registeration/',LucasaRegisterView.as_view(),name='register')
]
