from django.urls import path,include,re_path
from .views import GoogleLogin,ResendEmailConfirmationView,UserProfileView,ConfirmEmailView
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView
from .views import CustomPasswordResetView, CustomPasswordResetConfirmView



urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('confirm-email/', ConfirmEmailView.as_view(), name='confirm_email'),
    path('resend-confirmation/', ResendEmailConfirmationView.as_view(), name='resend_email_confirmation'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('password/reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
