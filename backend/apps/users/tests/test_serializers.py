from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import ClientProfile
from apps.users.serializers import RegisterSerializer
from apps.risk.serializers import ClientProfileAdminSerializer

User = get_user_model()

class RegisterSerializerTest(TestCase):
    def setUp(self):
        # Create a client profile for testing (account number will be auto-generated)
        self.client_profile = ClientProfile.objects.create(
            first_name='John',
            last_name='Doe',
            national_id='123456789',
            balance=5000.00
        )

    def test_valid_registration_data(self):
        """Test registration with valid data"""
        data = {
            'email': 'johndoe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123',
            'national_id': '123456789',
            'bank_account_number': self.client_profile.bank_account_number
        }
        
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.email, 'johndoe@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.role, 'CLIENT')
        self.assertEqual(user.clientprofile, self.client_profile)

    def test_registration_with_missing_email(self):
        """Test registration without email"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123',
            'national_id': '123456789',
            'bank_account_number': self.client_profile.bank_account_number
        }
        
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_registration_with_missing_first_name(self):
        """Test registration without first_name"""
        data = {
            'email': 'johndoe@example.com',
            'last_name': 'Doe',
            'password': 'password123',
            'national_id': '123456789',
            'bank_account_number': self.client_profile.bank_account_number
        }
        
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('first_name', serializer.errors)

    def test_registration_with_missing_last_name(self):
        """Test registration without last_name"""
        data = {
            'email': 'johndoe@example.com',
            'first_name': 'John',
            'password': 'password123',
            'national_id': '123456789',
            'bank_account_number': self.client_profile.bank_account_number
        }
        
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('last_name', serializer.errors)

    def test_registration_without_national_id(self):
        """Test registration without national_id"""
        data = {
            'email': 'johndoe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123',
            'bank_account_number': self.client_profile.bank_account_number
        }
        
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('national_id', serializer.errors)

    def test_registration_without_bank_account_number(self):
        """Test registration without bank_account_number"""
        data = {
            'email': 'johndoe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123',
            'national_id': '123456789'
        }
        
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('bank_account_number', serializer.errors)

    def test_registration_with_nonexistent_profile(self):
        """Test registration with non-existent profile"""
        data = {
            'email': 'johndoe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123',
            'national_id': '999999999',
            'bank_account_number': '99999999'
        }
        
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('No client profile found with the provided National ID and Bank Account Number combination', str(serializer.errors))

    def test_registration_with_mismatched_profile(self):
        """Test registration with mismatched national_id and bank_account_number"""
        data = {
            'email': 'johndoe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123',
            'national_id': '123456789',
            'bank_account_number': '99999999'  # Wrong account number
        }
        
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('No client profile found with the provided National ID and Bank Account Number combination', str(serializer.errors))

    def test_registration_with_already_linked_profile(self):
        """Test registration with profile already linked to a user"""
        # First, create a user and link it to the profile
        user = User.objects.create_user(
            email='existinguser@example.com',
            first_name='Existing',
            last_name='User',
            password='password123'
        )
        self.client_profile.user = user
        self.client_profile.save()
        
        # Try to register with the same profile
        data = {
            'email': 'johndoe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123',
            'national_id': '123456789',
            'bank_account_number': self.client_profile.bank_account_number
        }
        
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('This profile is already linked to a user account.', str(serializer.errors))

class ClientProfileAdminSerializerTest(TestCase):
    def setUp(self):
        self.client_profile = ClientProfile.objects.create(
            first_name='John',
            last_name='Doe',
            national_id='123456789',
            balance=5000.00
        )

    def test_valid_profile_data(self):
        """Test serializer with valid profile data"""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'national_id': '987654321',
            'balance': 10000.00
        }
        
        serializer = ClientProfileAdminSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_duplicate_national_id_validation(self):
        """Test validation with duplicate national_id"""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'national_id': '123456789',  # Same as existing
            'balance': 10000.00
        }
        
        serializer = ClientProfileAdminSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('national_id', serializer.errors)

    def test_update_without_duplicates(self):
        """Test updating profile without creating duplicates"""
        data = {
            'first_name': 'John Updated',
            'last_name': 'Doe',
            'national_id': '123456789',
            'balance': 7500.00
        }
        
        serializer = ClientProfileAdminSerializer(instance=self.client_profile, data=data)
        self.assertTrue(serializer.is_valid())

    def test_auto_generated_account_number_in_response(self):
        """Test that auto-generated account number is included in response"""
        serializer = ClientProfileAdminSerializer(self.client_profile)
        data = serializer.data
        
        self.assertIn('bank_account_number', data)
        self.assertIsNotNone(data['bank_account_number'])
        self.assertEqual(len(data['bank_account_number']), 8)

    def test_full_name_in_response(self):
        """Test that full_name is included in response"""
        serializer = ClientProfileAdminSerializer(self.client_profile)
        data = serializer.data
        
        self.assertIn('full_name', data)
        self.assertEqual(data['full_name'], 'John Doe')
