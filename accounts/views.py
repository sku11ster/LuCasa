from django.shortcuts import render
from dj_rest_auth.registration.views import RegisterView
from .serializers import LucasaRegisterSerializer

# Create your views here.
class LucasaRegisterView(RegisterView):
    serializer_class = LucasaRegisterSerializer