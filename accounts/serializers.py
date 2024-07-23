from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from .models import User

class LucasaRegisterSerializer(RegisterSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def custom_signup(self, request, user):
        user.user_type = self.validated_data.get('user_type', '')
        user.is_individual = self.validated_data.get('is_individual', True)
        user.company_name = self.validated_data.get('company_name', '')
        user.contact_number = self.validated_data.get('contact_number', '')
        user.profile_picture = self.validated_data.get('profile_picture', '')
        user.profile_banner = self.validated_data.get('profile_banner', '')
        user.address = self.validated_data.get('address', '')
        user.website = self.validated_data.get('website', '')
        user.bio = self.validated_data.get('bio', '')
        user.social_media_links = self.validated_data.get('social_media_links', '')
        user.save()