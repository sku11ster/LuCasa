from django.urls import reverse
from accounts.models import CustomUser
from rest_framework import status
from rest_framework.test import APITestCase
from allauth.account.models import EmailAddress
from django.core import mail
import re
# Create your tests here.

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='testpassword'
            )
        self.email_address = EmailAddress.objects.create(
            user=self.user,email='testuser@test.com',primary=True,verified = True
        )
        
        self.login_url = reverse('rest_login')
        self.login_data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(self.login_url, self.login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data['key']



    def tearDown(self):
        self.user.delete()
        self.email_address.delete()

    def test_login(self):
        url = reverse('rest_login')
        data = {'username':'testuser','password':'testpassword'}
        response = self.client.post(url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_registeration(self):
        url =reverse('rest_register')
        data = {'username':'testuser1','email':'testuser@test.com1','password1': 'tranew@password', 'password2': 'tranew@password','user_type':'seller'}
        response = self.client.post(url,data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        print(email)

        #token extraction from email
        match = re.search(r'account-confirm-email/([^/]+)/', email.body)
        confirmation_key = match.group(1)

        print("The key is:",confirmation_key)

        #email confirmation endpoint testing
        confirm_url = reverse('confirm_email')
        data = {'key':f'{confirmation_key}'}
        response = self.client.post(confirm_url,data)
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