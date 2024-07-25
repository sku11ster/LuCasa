from django.urls import reverse
from accounts.models import CustomUser
from rest_framework import status
from rest_framework.test import APITestCase
from allauth.account.models import EmailAddress

# Create your tests here.
class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='testpassword'
            )
        self.email_address = EmailAddress.objects.create(
            user=self.user,email='testuser@test.com',Primary=True,verified = True
        )
    def tearDown(self):
        self.user.delete()
        self.email_address.delete()

    def test_login(self):
        url = reverse('rest_login')
        data = {'username':'testuser','password':'testpassword'}
        response = self.client.post(url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_registeration(self):
        url =reverse('user_register')
        data = {'username':'testuser','email':'testuser@test.com','password1': 'newpassword', 'password2': 'newpassword','bio':'testpassword'}
        response = self.client.post(url,data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)

    def test_confirm_email(self):
        url = reverse('confirm_email',kwargs={'key':self.email_address.key})
        data = {'email':'testuser@test.com'}
        response = self.client.post(url,data)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_resend_confirmation(self):
            url = reverse('resend_email_confirmation')
            data = {'email': 'testuser@test.com'}
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_profile(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('user_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_password_reset(self):
        url = reverse('rest_password_reset')
        data = {'email': 'testuser@example.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)