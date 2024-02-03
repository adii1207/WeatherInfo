from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class UserRegistrationViewTests(APITestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com'
        )

    def test_registration_success(self): 
        url = reverse('user-registration')
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'email': 'new@example.com'
        }

        # Do not authenticate the user for registration
        response = self.client.post(url, data, format='json')

        # Check if the registration is successful (status code 201)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the number of users increased by 1
        self.assertEqual(User.objects.count(), 2)  # Change to 2 since we have the initial user created in setUp

        # Check that the new user has the correct username
        self.assertEqual(User.objects.get(username='newuser').username, 'newuser')

    def test_registration_fail(self):
        url = reverse('user-registration')
        data = {
            'username': '',  # Username is required
            'password': 'testpassword123',
            'email': 'test@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

class WeatherHistoricDataTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        self.url = reverse('weather-report-data')

    def test_access_denied_without_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
