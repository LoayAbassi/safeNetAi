from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from apps.users.models import ClientProfile

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        
        self.client_user = User.objects.create_user(
            email='client@test.com',
            first_name='Client',
            last_name='User',
            password='client123'
        )

    def test_user_creation_with_email(self):
        """Test that users can be created with email as username"""
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='password123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')

    def test_user_creation_without_email_fails(self):
        """Test that user creation fails without email"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                first_name='Test',
                last_name='User',
                password='password123'
            )

    def test_unique_email_validation(self):
        """Test that duplicate emails raise validation error"""
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='admin@test.com',  # Same as existing
                first_name='Test',
                last_name='User',
                password='password123'
            )

    def test_user_string_representation(self):
        """Test the string representation of User"""
        self.assertEqual(str(self.admin_user), 'admin@test.com')

class ClientProfileModelTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        
        self.client_profile = ClientProfile.objects.create(
            first_name='John',
            last_name='Doe',
            national_id='123456789',
            balance=5000.00
        )

    def test_client_profile_creation_with_auto_generated_account(self):
        """Test that client profile can be created with auto-generated bank account number"""
        profile = ClientProfile.objects.create(
            first_name='Jane',
            last_name='Smith',
            national_id='987654321',
            balance=10000.00
        )
        self.assertEqual(profile.first_name, 'Jane')
        self.assertEqual(profile.last_name, 'Smith')
        self.assertEqual(profile.national_id, '987654321')
        # Bank account number should be auto-generated
        self.assertIsNotNone(profile.bank_account_number)
        self.assertEqual(len(profile.bank_account_number), 8)
        self.assertTrue(profile.bank_account_number.isdigit())

    def test_unique_national_id_validation(self):
        """Test that duplicate national_id raises validation error"""
        with self.assertRaises(ValidationError):
            ClientProfile.objects.create(
                first_name='Duplicate',
                last_name='User',
                national_id='123456789',  # Same as existing
                balance=1000.00
            )

    def test_unique_bank_account_number_auto_generation(self):
        """Test that auto-generated bank account numbers are unique"""
        profile1 = ClientProfile.objects.create(
            first_name='User',
            last_name='One',
            national_id='111111111',
            balance=1000.00
        )
        
        profile2 = ClientProfile.objects.create(
            first_name='User',
            last_name='Two',
            national_id='222222222',
            balance=2000.00
        )
        
        # Both should have different account numbers
        self.assertNotEqual(profile1.bank_account_number, profile2.bank_account_number)
        self.assertIsNotNone(profile1.bank_account_number)
        self.assertIsNotNone(profile2.bank_account_number)

    def test_update_with_duplicate_national_id(self):
        """Test that updating with existing national_id raises validation error"""
        profile2 = ClientProfile.objects.create(
            first_name='Jane',
            last_name='Smith',
            national_id='987654321',
            balance=10000.00
        )
        
        profile2.national_id = '123456789'  # Same as existing profile
        with self.assertRaises(ValidationError):
            profile2.save()

    def test_valid_update(self):
        """Test that valid updates work correctly"""
        self.client_profile.first_name = 'John Updated'
        self.client_profile.balance = 7500.00
        self.client_profile.save()
        
        updated_profile = ClientProfile.objects.get(id=self.client_profile.id)
        self.assertEqual(updated_profile.first_name, 'John Updated')
        self.assertEqual(updated_profile.balance, 7500.00)

    def test_string_representation(self):
        """Test the string representation of ClientProfile"""
        self.assertEqual(str(self.client_profile), 'John Doe (123456789)')

    def test_full_name_property(self):
        """Test the full_name property"""
        self.assertEqual(self.client_profile.full_name, 'John Doe')

    def test_manual_bank_account_number_assignment(self):
        """Test that manually assigned bank account numbers work correctly"""
        profile = ClientProfile.objects.create(
            first_name='Manual',
            last_name='User',
            national_id='555555555',
            bank_account_number='12345678',
            balance=5000.00
        )
        self.assertEqual(profile.bank_account_number, '12345678')
