from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from apps.users.models import ClientProfile, generate_otp
from apps.users.email_service import EmailService

User = get_user_model()

class EmailVerificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='password123'
        )

    def test_otp_generation(self):
        """Test that OTP generation creates 6-digit numbers"""
        otp = generate_otp()
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())
        self.assertTrue(100000 <= int(otp) <= 999999)

    def test_user_email_verification_fields(self):
        """Test that user has email verification fields"""
        self.assertFalse(self.user.is_email_verified)
        self.assertIsNone(self.user.email_otp)

    def test_user_email_verification_update(self):
        """Test updating email verification status"""
        otp = generate_otp()
        self.user.email_otp = otp
        self.user.is_email_verified = True
        self.user.save()
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)
        self.assertEqual(self.user.email_otp, otp)

class EmailServiceTest(TestCase):
    @patch('apps.users.email_service.os.getenv')
    def test_email_service_configured_with_credentials(self, mock_getenv):
        """Test email service configuration when credentials are available"""
        mock_getenv.side_effect = lambda x: {
            'GMAIL_EMAIL': 'test@gmail.com',
            'GMAIL_APP_PASSWORD': 'password123'
        }.get(x)
        
        email_service = EmailService()
        self.assertTrue(email_service.is_configured())

    @patch('apps.users.email_service.os.getenv')
    def test_email_service_configured_without_credentials(self, mock_getenv):
        """Test email service configuration when credentials are missing"""
        mock_getenv.return_value = None
        
        email_service = EmailService()
        self.assertFalse(email_service.is_configured())

    @patch('apps.users.email_service.smtplib.SMTP')
    @patch('apps.users.email_service.os.getenv')
    def test_send_otp_email_success(self, mock_getenv, mock_smtp):
        """Test successful OTP email sending"""
        # Mock environment variables
        mock_getenv.side_effect = lambda x: {
            'GMAIL_EMAIL': 'test@gmail.com',
            'GMAIL_APP_PASSWORD': 'password123'
        }.get(x)
        
        # Mock SMTP
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        email_service = EmailService()
        result = email_service.send_otp_email('user@example.com', '123456')
        
        self.assertTrue(result)
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@gmail.com', 'password123')
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch('apps.users.email_service.smtplib.SMTP')
    @patch('apps.users.email_service.os.getenv')
    def test_send_otp_email_failure(self, mock_getenv, mock_smtp):
        """Test OTP email sending failure"""
        # Mock environment variables
        mock_getenv.side_effect = lambda x: {
            'GMAIL_EMAIL': 'test@gmail.com',
            'GMAIL_APP_PASSWORD': 'password123'
        }.get(x)
        
        # Mock SMTP to raise exception
        mock_smtp.side_effect = Exception("SMTP Error")
        
        email_service = EmailService()
        result = email_service.send_otp_email('user@example.com', '123456')
        
        self.assertFalse(result)

class EmailVerificationAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create a client profile for testing
        self.client_profile = ClientProfile.objects.create(
            first_name='John',
            last_name='Doe',
            national_id='123456789',
            balance=5000.00
        )

    @patch('apps.users.serializers.EmailService')
    def test_registration_generates_otp(self, mock_email_service):
        """Test that registration generates OTP and sends email"""
        mock_service_instance = MagicMock()
        mock_service_instance.is_configured.return_value = True
        mock_service_instance.send_otp_email.return_value = True
        mock_email_service.return_value = mock_service_instance
        
        data = {
            'email': 'johndoe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123',
            'national_id': '123456789',
            'bank_account_number': self.client_profile.bank_account_number
        }
        
        response = self.client.post('/api/auth/register/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'OTP sent to your email')
        
        # Verify user was created with OTP
        user = User.objects.get(email='johndoe@example.com')
        self.assertIsNotNone(user.email_otp)
        self.assertEqual(len(user.email_otp), 6)
        self.assertFalse(user.is_email_verified)
        
        # Verify email service was called
        mock_service_instance.send_otp_email.assert_called_once_with('johndoe@example.com', user.email_otp)

    def test_otp_verification_success(self):
        """Test successful OTP verification"""
        # Create user with OTP
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='password123',
            email_otp='123456',
            is_email_verified=False
        )
        
        data = {
            'email': 'test@example.com',
            'otp': '123456'
        }
        
        response = self.client.post('/api/verify-otp/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Email verified successfully')
        
        # Verify user was updated
        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)
        self.assertIsNone(user.email_otp)

    def test_otp_verification_invalid_otp(self):
        """Test OTP verification with invalid OTP"""
        # Create user with OTP
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='password123',
            email_otp='123456',
            is_email_verified=False
        )
        
        data = {
            'email': 'test@example.com',
            'otp': '654321'  # Wrong OTP
        }
        
        response = self.client.post('/api/verify-otp/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid OTP', str(response.data))
        
        # Verify user was not updated
        user.refresh_from_db()
        self.assertFalse(user.is_email_verified)
        self.assertEqual(user.email_otp, '123456')

    def test_otp_verification_nonexistent_user(self):
        """Test OTP verification with non-existent user"""
        data = {
            'email': 'nonexistent@example.com',
            'otp': '123456'
        }
        
        response = self.client.post('/api/verify-otp/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('User with this email does not exist', str(response.data))

    def test_otp_verification_already_verified(self):
        """Test OTP verification for already verified user"""
        # Create verified user
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='password123',
            email_otp='123456',
            is_email_verified=True
        )
        
        data = {
            'email': 'test@example.com',
            'otp': '123456'
        }
        
        response = self.client.post('/api/verify-otp/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email is already verified', str(response.data))

    def test_otp_verification_no_otp(self):
        """Test OTP verification for user without OTP"""
        # Create user without OTP
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='password123',
            email_otp=None,
            is_email_verified=False
        )
        
        data = {
            'email': 'test@example.com',
            'otp': '123456'
        }
        
        response = self.client.post('/api/verify-otp/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No OTP found for this user', str(response.data))

    def test_login_blocked_unverified_user(self):
        """Test that login is blocked for unverified users"""
        # Create unverified user
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='password123',
            is_email_verified=False
        )
        
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        
        response = self.client.post('/api/auth/login/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Please verify your email first', str(response.data))

    def test_login_allowed_verified_user(self):
        """Test that login is allowed for verified users"""
        # Create verified user
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='password123',
            is_email_verified=True
        )
        
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        
        response = self.client.post('/api/auth/login/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_otp_verification_invalid_email_format(self):
        """Test OTP verification with invalid email format"""
        data = {
            'email': 'invalid-email',
            'otp': '123456'
        }
        
        response = self.client.post('/api/verify-otp/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_otp_verification_invalid_otp_format(self):
        """Test OTP verification with invalid OTP format"""
        data = {
            'email': 'test@example.com',
            'otp': '123'  # Too short
        }
        
        response = self.client.post('/api/verify-otp/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('otp', response.data)

    def test_otp_verification_missing_fields(self):
        """Test OTP verification with missing fields"""
        # Test missing email
        data = {
            'otp': '123456'
        }
        
        response = self.client.post('/api/verify-otp/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
        # Test missing OTP
        data = {
            'email': 'test@example.com'
        }
        
        response = self.client.post('/api/verify-otp/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('otp', response.data)

    @patch('apps.users.serializers.EmailService')
    def test_registration_email_service_not_configured(self, mock_email_service):
        """Test registration when email service is not configured"""
        mock_service_instance = MagicMock()
        mock_service_instance.is_configured.return_value = False
        mock_email_service.return_value = mock_service_instance
        
        data = {
            'email': 'johndoe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123',
            'national_id': '123456789',
            'bank_account_number': self.client_profile.bank_account_number
        }
        
        response = self.client.post('/api/auth/register/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'OTP sent to your email')
        
        # Verify user was still created with OTP
        user = User.objects.get(email='johndoe@example.com')
        self.assertIsNotNone(user.email_otp)
        self.assertFalse(user.is_email_verified)
        
        # Verify email service was not called
        mock_service_instance.send_otp_email.assert_not_called()
