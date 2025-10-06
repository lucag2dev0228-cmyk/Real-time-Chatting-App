from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import User

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        """Test user creation with custom fields"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_online)
    
    def test_user_full_name_property(self):
        """Test full_name property"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        self.assertEqual(user.full_name, 'John Doe')
    
    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        expected_str = f"{user.first_name} {user.last_name} ({user.email})"
        self.assertEqual(str(user), expected_str)


class UserRegistrationAPITest(APITestCase):
    def test_user_registration_success(self):
        """Test successful user registration"""
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)
        self.assertTrue('user' in response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertEqual(response.data['user']['first_name'], 'John')
        self.assertEqual(response.data['user']['last_name'], 'Doe')
    
    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        User.objects.create_user(
            username='testuser1',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        url = reverse('register')
        data = {
            'username': 'testuser2',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Jane',
            'last_name': 'Smith'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_missing_fields(self):
        """Test registration with missing required fields"""
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
            # Missing first_name and last_name
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_invalid_email(self):
        """Test registration with invalid email format"""
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
    
    def test_user_login_success(self):
        """Test successful user login"""
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.assertTrue('user' in response.data)
        self.assertTrue(response.data['user']['is_online'])
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login_nonexistent_user(self):
        """Test login with non-existent user"""
        url = reverse('login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.token = self.user.auth_token.key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
    
    def test_get_user_profile(self):
        """Test getting user profile"""
        url = reverse('user_profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['first_name'], 'John')
        self.assertEqual(response.data['last_name'], 'Doe')
    
    def test_get_user_profile_unauthorized(self):
        """Test getting user profile without authentication"""
        self.client.credentials()  # Remove auth
        
        url = reverse('user_profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserLogoutAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.token = self.user.auth_token.key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
    
    def test_user_logout_success(self):
        """Test successful user logout"""
        url = reverse('logout')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logout successful')
        
        # Check that user is marked as offline
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_online)
    
    def test_user_logout_unauthorized(self):
        """Test logout without authentication"""
        self.client.credentials()  # Remove auth
        
        url = reverse('logout')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UsersListAPITest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='user1@example.com',
            password='testpass123',
            first_name='User',
            last_name='One'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='user2@example.com',
            password='testpass123',
            first_name='User',
            last_name='Two'
        )
        
        self.token = self.user1.auth_token.key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
    
    def test_get_users_list(self):
        """Test getting list of all users"""
        url = reverse('users_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Check that users are ordered by online status first
        user_emails = [user['email'] for user in response.data]
        self.assertIn('user1@example.com', user_emails)
        self.assertIn('user2@example.com', user_emails)
    
    def test_get_users_list_unauthorized(self):
        """Test getting users list without authentication"""
        self.client.credentials()  # Remove auth
        
        url = reverse('users_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
