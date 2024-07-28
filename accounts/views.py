from django.shortcuts import render
from dj_rest_auth.registration.views import RegisterView,SocialLoginView
from .serializers import CustomUserRegisterSerializer,OwnerProfileSerializer
from rest_framework import generics,status
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_framework.views import APIView
from rest_framework.response import Response
from allauth.account.utils import send_email_confirmation
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated,AllowAny
from .serializers import CustomUserRegisterSerializer,CustomUserSerializer
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC,EmailAddress
from django.contrib.auth.models import User
from dj_rest_auth.views import PasswordResetConfirmView
from property.models import Property
from django.db.models import Count

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

# Create your views here.
class LucasaRegisterView(RegisterView):
    serializer_class = CustomUserRegisterSerializer
# Confirm email view
class ConfirmEmailView(APIView):

    def post(self, request, *args, **kwargs):
        confirmation_key = request.data.get('key')
        if not confirmation_key:
            return Response({"detail": "No confirmation key provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            email_confirmation = EmailConfirmationHMAC.from_key(confirmation_key)
        except EmailConfirmation.DoesNotExist:
            email_confirmation = EmailConfirmation.objects.filter(key=confirmation_key.lower()).first()

        if not email_confirmation:
            return Response({"detail": "Invalid confirmation key"}, status=status.HTTP_400_BAD_REQUEST)

        email_confirmation.confirm(request)
        return Response({"detail": "Email confirmed successfully"}, status=status.HTTP_200_OK)

# User mail reconfirmation endpoint
User = get_user_model()
class ResendEmailConfirmationView(APIView):
    permission_classes =[IsAuthenticated]
    def post(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        if email:
            try:
                user = User.objects.get(email=email)
                email_address = EmailAddress.objects.get(user=user, email=email)
                if email_address.verified:
                    return Response({"detail": "This email is already verified."}, status=status.HTTP_400_BAD_REQUEST)
                send_email_confirmation(request, user, signup=False)
                return Response({"detail": "Email confirmation sent."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"detail": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)
            except EmailAddress.DoesNotExist:
                return Response({"detail": "Email address does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
    
# User profile data endpoint
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, identifier=None, *args, **kwargs):
        user = None  # Initialize user variable
        if identifier:
            if identifier.isdigit():
                # Handle as ID
                try:
                    user = User.objects.get(pk=identifier)
                except User.DoesNotExist:
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                # Handle as username
                try:
                    user = User.objects.get(username=identifier)
                except User.DoesNotExist:
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
        
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize user data
        serializer = CustomUserSerializer(user)
        
        # Count properties by type
        property_counts = Property.objects.filter(user=user).values('property_type').annotate(count=Count('property_type'))
        
        # Construct response data
        response_data = serializer.data
        response_data['property_counts'] = list(property_counts)

        return Response(response_data, status=status.HTTP_200_OK)

        
class PropertyDetailPageOwnerView(APIView):
    permission_classes = [AllowAny]
    def get(self,request,id=None,*args, **kwargs):
        if id:
            try:
                user = User.objects.get(id = id)
                serializer = OwnerProfileSerializer(user)
            except User.DoesNotExist:
                return Response({'error':'No Owner Found'})
            
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            return Response({"detail": "Password reset unsuccessful. The password reset link was invalid, possibly because it has already been used. Please request a new password reset."}, status=response.status_code)
        return Response({"detail": "Password has been reset with the new password."}, status=response.status_code)

class AccountVerificationStatusView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        user = request.user
        try:
            email_address = EmailAddress.objects.get(user=user,primary=True)
            is_verified = email_address.verified
            return Response({'is_verified': is_verified}, status=status.HTTP_200_OK)
        except EmailAddress.DoesNotExist:
            return Response({'error':'Primary email not found for user'},status=status.HTTP_404_NOT_FOUND)

class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    lookup_field = 'username'

    def get_object(self):
        return self.request.user
    

# class OwnerDetailView(APIVIEW):