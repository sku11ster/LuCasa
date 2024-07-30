from rest_framework import serializers
from django.contrib.auth.models import AbstractUser
from .models import CustomUser  # Adjust the import path according to your project structure
from allauth.account.models import EmailAddress
from django.contrib.auth.forms import PasswordResetForm

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CustomUser  
from django.contrib.auth import authenticate


class CustomUserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'password', 'user_type', 'is_individual',
            'company_name', 'contact', 'address', 'website', 'bio', 
            'social_links', 'profile_picture', 'profile_banner'
        )
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data.get('user_type', 'buyer'),
            is_individual=validated_data.get('is_individual', True),
            company_name=validated_data.get('company_name', ''),
            contact=validated_data.get('contact', ''),
            address=validated_data.get('address', ''),
            website=validated_data.get('website', ''),
            bio=validated_data.get('bio', ''),
            social_links=validated_data.get('social_links', {}),
            profile_picture=validated_data.get('profile_picture', '/profile_pics/default.png'),
            profile_banner=validated_data.get('profile_banner', '/profile_banner/default.png'),
        )
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
