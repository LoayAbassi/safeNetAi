from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.users.models import ClientProfile

User = get_user_model()

class AdminViewsTest(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            password='admin123',
            role='ADMIN'
        )
        
        # Create regular client user
        self.client_user = User.objects.create_user(
            email='client@test.com',
            first_name='Client',
            last_name='User',
            password='client123',
            role='CLIENT'
        )
        
        # Create a client profile
        self.client_profile = ClientProfile.objects.create(
            first_name='John',
            last_name='Doe',
            national_id='123456789',
            balance=5000.00
        )
        
        self.client = APIClient()

    def test_admin_can_create_client_profile(self):
        """Test that admin can create client profiles with auto-generated account number"""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'national_id': '987654321',
            'balance': 10000.00
        }
        
        response = self.client.post('/api/admin/clients/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify the profile was created
        profile = ClientProfile.objects.get(national_id='987654321')
        self.assertEqual(profile.first_name, 'Jane')
        self.assertEqual(profile.last_name, 'Smith')
        # Bank account number should be auto-generated
        self.assertIsNotNone(profile.bank_account_number)
        self.assertEqual(len(profile.bank_account_number), 8)

    def test_client_cannot_create_client_profile(self):
        """Test that regular clients cannot create client profiles"""
        self.client.force_authenticate(user=self.client_user)
        
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'national_id': '987654321',
            'balance': 10000.00
        }
        
        response = self.client.post('/api/admin/clients/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_client_profile(self):
        """Test that admin can update client profiles"""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'first_name': 'John Updated',
            'last_name': 'Doe',
            'national_id': '123456789',
            'balance': 7500.00
        }
        
        response = self.client.put(f'/api/admin/clients/{self.client_profile.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the profile was updated
        self.client_profile.refresh_from_db()
        self.assertEqual(self.client_profile.first_name, 'John Updated')
        self.assertEqual(self.client_profile.balance, 7500.00)

    def test_client_cannot_update_client_profile(self):
        """Test that regular clients cannot update client profiles"""
        self.client.force_authenticate(user=self.client_user)
        
        data = {
            'first_name': 'John Updated',
            'last_name': 'Doe',
            'national_id': '123456789',
            'balance': 7500.00
        }
        
        response = self.client.put(f'/api/admin/clients/{self.client_profile.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_client_profile(self):
        """Test that admin can delete client profiles"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.delete(f'/api/admin/clients/{self.client_profile.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify the profile was deleted
        self.assertFalse(ClientProfile.objects.filter(id=self.client_profile.id).exists())

    def test_client_cannot_delete_client_profile(self):
        """Test that regular clients cannot delete client profiles"""
        self.client.force_authenticate(user=self.client_user)
        
        response = self.client.delete(f'/api/admin/clients/{self.client_profile.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_duplicate_national_id_creation(self):
        """Test that creating profile with duplicate national_id fails"""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'national_id': '123456789',  # Same as existing
            'balance': 10000.00
        }
        
        response = self.client.post('/api/admin/clients/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('national_id', response.data)

    def test_admin_search_clients(self):
        """Test admin search functionality"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/api/admin/clients/search/?q=john')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], 'John')

    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access admin endpoints"""
        response = self.client.get('/api/admin/clients/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auto_generated_account_numbers_are_unique(self):
        """Test that auto-generated account numbers are unique"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create multiple profiles
        profiles_data = [
            {'first_name': 'User', 'last_name': 'One', 'national_id': '111111111', 'balance': 1000.00},
            {'first_name': 'User', 'last_name': 'Two', 'national_id': '222222222', 'balance': 2000.00},
            {'first_name': 'User', 'last_name': 'Three', 'national_id': '333333333', 'balance': 3000.00},
        ]
        
        account_numbers = set()
        for data in profiles_data:
            response = self.client.post('/api/admin/clients/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            profile = ClientProfile.objects.get(national_id=data['national_id'])
            account_numbers.add(profile.bank_account_number)
        
        # All account numbers should be unique
        self.assertEqual(len(account_numbers), 3)

    def test_search_by_first_name(self):
        """Test search by first name"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/api/admin/clients/search/?q=john')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], 'John')

    def test_search_by_last_name(self):
        """Test search by last name"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/api/admin/clients/search/?q=doe')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['last_name'], 'Doe')

    def test_search_by_national_id(self):
        """Test search by national ID"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/api/admin/clients/search/?q=123456789')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['national_id'], '123456789')
