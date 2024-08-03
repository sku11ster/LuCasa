from django.urls import path,include,re_path
from .views import SignUpView,ResendEmailConfirmationView,UserProfileView,ConfirmEmailView,PropertyDetailPageOwnerView
# from dj_rest_auth.views import PasswordResetView,PasswordResetConfirmView

from .views import PasswordResetRequestView, PasswordResetView


from .views import AccountVerificationStatusView,UserProfileUpdateView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
    TokenVerifyView,
    TokenBlacklistView
)

urlpatterns = [

    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),

    # path('signup/', include('allauth.urls')),
    path('signup/', SignUpView.as_view(),name='user-register'),
    
    path('activate/<str:key>/', ConfirmEmailView.as_view(), name='confirm_email'),
    path('resend-confirmation/', ResendEmailConfirmationView.as_view(), name='resend_email_confirmation'),
    
    # path('password/reset/', PasswordResetView.as_view(), name='password_reset'),
    # path('password/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/', PasswordResetView.as_view(), name='password_reset'),

    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/edit', UserProfileUpdateView.as_view(), name='rest_user_details'),
    path('profile/<str:identifier>/', UserProfileView.as_view(), name='user_profile_detail'),
    path('<int:id>/',PropertyDetailPageOwnerView.as_view(),name='owner_card_info'),
    path('email-status/',AccountVerificationStatusView.as_view(),name='email_status'),

]
