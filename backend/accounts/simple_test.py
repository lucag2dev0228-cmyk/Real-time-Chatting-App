from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class SimpleUserTest(TestCase):
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

