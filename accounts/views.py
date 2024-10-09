from django.shortcuts import render
from .serializers import CustomUserRegisterSerializer,OwnerProfileSerializer

from rest_framework import generics,status,serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny

from allauth.account.utils import send_email_confirmation
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC,EmailAddress


from .serializers import CustomUserRegisterSerializer,CustomUserSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from property.models import Property
from django.db.models import Count

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils.encoding import force_str,force_bytes
from .models import PasswordResetToken
from property.models import Favorite
from property.serializers import FavoriteSerializer

# Create your views here.
class SignUpView(generics.CreateAPIView):
    serializer_class = CustomUserRegisterSerializer
    def post(self,request,*args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_email_confirmation(request, user)
            return Response({"message":"User created successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

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
        
        #  user data
        serializer = CustomUserSerializer(user)
        # Concatenating Properties count 
        property_counts = Property.objects.filter(user=user).values('property_type').annotate(count=Count('property_type'))
        
        response_data = serializer.data
        response_data['property_counts'] = list(property_counts)

        # Concatenating Favorite Properties
        favorite_properties = Favorite.objects.filter(user=user)
        favorite_serializer = FavoriteSerializer(favorite_properties,many=True)
        response_data['favorite_properties'] = favorite_serializer.data

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

token_generator = PasswordResetTokenGenerator()

# Custom Password Reset Request view
class PasswordResetRequestView(APIView):
    """
    Handles password reset. Sends an email with a password reset link if the email exists.
    """

    permission_classes =[AllowAny]

    def post(self,request,*args, **kwargs):
        email = request.data.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
            except:
                return Response({'error':'Email not found'},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error':'Email is required'},status=status.HTTP_400_BAD_REQUEST)
        
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        PasswordResetToken.objects.create(user=user,token=token)

        link = settings.FRONTEND_URL
        reset_link = f"{link}/account/password/reset/confirm/{uid}/{token}/"


        # mail
        subject = "Password Reset Request"
        message = render_to_string('registration/password_reset_email.html',{
            'user': user,
            'reset_link': reset_link,
        })
        send_mail(subject,message,settings.DEFAULT_FROM_EMAIL,[email])
        return JsonResponse({'message': 'Password reset link sent.'})
    

class PasswordResetView(APIView):
    """
    Handles password reset. Validates the reset token and updates the password.
    """

    permission_classes =[AllowAny]
    
    def post(self,request,*args, **kwargs):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not uid or not token or not new_password:
            return Response({'error':'All fields are required'},status=status.HTTP_400_BAD_REQUEST)
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return JsonResponse({'message': 'Invalid link or user does not exist.'}, status=400)

        try:
            reset_token = PasswordResetToken.objects.get(user=user, token=token)
        except PasswordResetToken.DoesNotExist:
            return JsonResponse({'message': 'Invalid or expired token.'}, status=400)

        if reset_token.is_expired():
            return JsonResponse({'message': 'Token has expired.'}, status=400)

        if not token_generator.check_token(user, token):
            return JsonResponse({'message': 'Invalid token.'}, status=400)

        user.set_password(new_password)
        user.save()
        reset_token.delete()

        return JsonResponse({'message': 'Password successfully reset.'},status=200)