from django.shortcuts import render
from dj_rest_auth.registration.views import RegisterView,SocialLoginView
from .serializers import CustomUserRegisterSerializer
from rest_framework import generics, permissions,status
from dj_rest_auth.views import PasswordResetView,PasswordResetConfirmView

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_framework.views import APIView
from rest_framework.response import Response
from allauth.account.utils import send_email_confirmation

from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomUserRegisterSerializer,CustomUserSerializer
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC,EmailAddress
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError



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

    def get(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)
    
# # User Password reset endpoint
# class UserPasswordResetView(APIView):
class CustomPasswordResetView(PasswordResetView):
    """
    Custom Password Reset View
    """
    def post(self, request, *args, **kwargs):
        """
        Handle POST request for password reset.
        """
        email = request.data.get('email')
        if not email:
            return Response({"email": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()
        if user:
            # Send email with reset link
            subject = "Password Reset Request"
            email_template_name = "password_reset_email.html"
            context = {
                'email': email,
                'uid': urlsafe_base64_encode(user.pk),
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
                'domain': request.get_host(),
                'site_name': 'My Site',
            }
            # Render email template here or use Django's built-in email
            send_mail(
                subject,
                f"Please click the link to reset your password: http://{context['domain']}/password/reset/confirm/{context['uid']}/{context['token']}/",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        return Response({"message": "Password reset link has been sent."}, status=status.HTTP_200_OK)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Custom Password Reset Confirm View
    """
    def post(self, request, *args, **kwargs):
        """
        Handle POST request for password reset confirmation.
        """
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not uidb64 or not token or not new_password:
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError("Invalid user or token.")

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password has been reset."}, status=status.HTTP_200_OK)