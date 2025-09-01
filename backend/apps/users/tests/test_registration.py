from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User, EmailOTP
from apps.risk.models import ClientProfile

class RegistrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create a client profile for testing
        self.client_profile = ClientProfile.objects.create(
            first_name="John",
            last_name="Doe",
            national_id="123456789",
            bank_account_number="12345678",
            balance=1000.00
        )
    
    def test_successful_registration(self):
        """Test successful user registration"""
        url = reverse('register')
        data = {
            'email': 'john.doe@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'national_id': '123456789',
            'bank_account_number': '12345678'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        
        # Check that user was created
        user = User.objects.get(email='john.doe@example.com')
        self.assertFalse(user.is_email_verified)
        
        # Check that OTP was created
        otp = EmailOTP.objects.filter(user=user).first()
        self.assertIsNotNone(otp)
    
    def test_registration_with_mismatched_profile(self):
        """Test registration with mismatched profile data"""
        url = reverse('register')
        data = {
            'email': 'john.doe@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Jane',  # Different name
            'last_name': 'Doe',
            'national_id': '123456789',
            'bank_account_number': '12345678'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Account verification failed', str(response.data))
    
    def test_registration_with_nonexistent_profile(self):
        """Test registration with non-existent profile"""
        url = reverse('register')
        data = {
            'email': 'john.doe@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'national_id': '999999999',  # Non-existent
            'bank_account_number': '87654321'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Account verification failed', str(response.data))

class OTPVerificationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create a client profile
        self.client_profile = ClientProfile.objects.create(
            first_name="John",
            last_name="Doe",
            national_id="123456789",
            bank_account_number="12345678",
            balance=1000.00
        )
        
        # Create a user
        self.user = User.objects.create_user(
            email='john.doe@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            is_email_verified=False
        )
        
        # Create an OTP
        self.otp = EmailOTP.objects.create(
            user=self.user,
            otp='123456',
            expires_at='2024-12-31T23:59:59Z'
        )
    
    def test_successful_otp_verification(self):
        """Test successful OTP verification"""
        url = reverse('verify-otp')
        data = {
            'email': 'john.doe@example.com',
            'otp': '123456'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        
        # Check that user is now verified
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)
        
        # Check that profile is linked
        self.client_profile.refresh_from_db()
        self.assertEqual(self.client_profile.user, self.user)
    
    def test_invalid_otp(self):
        """Test OTP verification with invalid OTP"""
        url = reverse('verify-otp')
        data = {
            'email': 'john.doe@example.com',
            'otp': '999999'  # Invalid OTP
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid OTP', str(response.data))

class LoginTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create a verified user
        self.user = User.objects.create_user(
            email='john.doe@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            is_email_verified=True
        )
    
    def test_successful_login(self):
        """Test successful login"""
        url = reverse('login')
        data = {
            'email': 'john.doe@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
    
    def test_login_with_unverified_email(self):
        """Test login with unverified email"""
        self.user.is_email_verified = False
        self.user.save()
        
        url = reverse('login')
        data = {
            'email': 'john.doe@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email not verified', str(response.data))
