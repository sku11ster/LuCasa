from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.contrib.auth.models import AbstractUser
from .models import CustomUser  # Adjust the import path according to your project structure
from allauth.account.models import EmailAddress
from django.contrib.auth.forms import PasswordResetForm

from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CustomUser  # Replace with your actual import if needed

class CustomUserRegisterSerializer(RegisterSerializer):
    """
    Serializer for registering a new user account.
    """
    first_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    user_type = serializers.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES)
    is_individual = serializers.BooleanField(required=False)
    company_name = serializers.CharField(max_length=255, required=False, allow_null=True)
    contact = serializers.CharField(max_length=15, required=False, allow_null=True)
    address = serializers.CharField(allow_blank=True, required=False)
    website = serializers.CharField(allow_blank=True, required=False)
    bio = serializers.CharField(allow_blank=True, required=False)
    social_links = serializers.JSONField(required=False)
    profile_picture = serializers.ImageField(use_url=True, required=False, allow_null=True)
    profile_banner = serializers.ImageField(use_url=True, required=False, allow_null=True)


    def save(self, request):
        user = super().save(request)
        user.first_name = self.validated_data.get('first_name', user.first_name)
        user.last_name = self.validated_data.get('last_name', user.last_name)
        user.user_type = self.validated_data.get('user_type', user.user_type)
        user.is_individual = self.validated_data.get('is_individual', user.is_individual)
        user.company_name = self.validated_data.get('company_name', user.company_name)
        user.contact = self.validated_data.get('contact', user.contact)
        user.address = self.validated_data.get('address', user.address)
        user.website = self.validated_data.get('website', user.website)
        user.bio = self.validated_data.get('bio', user.bio)
        user.social_links = self.validated_data.get('social_links', user.social_links)
        user.profile_picture = self.validated_data.get('profile_picture', '/profile_pics/default.png')
        user.profile_banner = self.validated_data.get('profile_banner', '/profile_banner/default.png')

        user.save()
        return user

    

class CustomUserSerializer(serializers.ModelSerializer):
    email_verified = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'user_type', 'is_individual', 'company_name', 'contact', 'address', 'website', 'bio', 'social_links', 'profile_picture', 'profile_banner', 'email_verified']
        extra_kwargs = {
            'email': {'read_only': True} 
        }

    def get_email_verified(self, obj):
        email_address = EmailAddress.objects.filter(user=obj, email=obj.email).first()
        return email_address.verified if email_address else False

class OwnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'profile_picture']