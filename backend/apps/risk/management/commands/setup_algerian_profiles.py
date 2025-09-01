from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.risk.models import ClientProfile
from decimal import Decimal
import json
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Setup 20 Algerian client profiles with realistic data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up Algerian client profiles...'))
        
        # Algerian client data
        algerian_clients = [
            {
                'first_name': 'Ahmed',
                'last_name': 'Benali',
                'email': 'ahmed.benali@example.com',
                'national_id': '1234567890123456',
                'balance': Decimal('150000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Yasmine',
                'last_name': 'Boudiaf',
                'email': 'yasmine.boudiaf@example.com',
                'national_id': '1234567890123457',
                'balance': Decimal('89000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Karim',
                'last_name': 'Mekki',
                'email': 'karim.mekki@example.com',
                'national_id': '1234567890123458',
                'balance': Decimal('220000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Leila',
                'last_name': 'Khelifi',
                'email': 'leila.khelifi@example.com',
                'national_id': '1234567890123459',
                'balance': Decimal('75000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Sofiane',
                'last_name': 'Belkacem',
                'email': 'sofiane.belkacem@example.com',
                'national_id': '1234567890123460',
                'balance': Decimal('180000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Amel',
                'last_name': 'Haddad',
                'email': 'amel.haddad@example.com',
                'national_id': '1234567890123461',
                'balance': Decimal('95000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Rachid',
                'last_name': 'Ould',
                'email': 'rachid.ould@example.com',
                'national_id': '1234567890123462',
                'balance': Decimal('320000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Nadia',
                'last_name': 'Cherif',
                'email': 'nadia.cherif@example.com',
                'national_id': '1234567890123463',
                'balance': Decimal('120000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Samir',
                'last_name': 'Bensaid',
                'email': 'samir.bensaid@example.com',
                'national_id': '1234567890123464',
                'balance': Decimal('250000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Farah',
                'last_name': 'Djemai',
                'email': 'farah.djemai@example.com',
                'national_id': '1234567890123465',
                'balance': Decimal('85000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Nabil',
                'last_name': 'Saadi',
                'email': 'nabil.saadi@example.com',
                'national_id': '1234567890123466',
                'balance': Decimal('175000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Selma',
                'last_name': 'Touati',
                'email': 'selma.touati@example.com',
                'national_id': '1234567890123467',
                'balance': Decimal('110000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Mourad',
                'last_name': 'Fekir',
                'email': 'mourad.fekir@example.com',
                'national_id': '1234567890123468',
                'balance': Decimal('280000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Hanane',
                'last_name': 'Boulahdour',
                'email': 'hanane.boulahdour@example.com',
                'national_id': '1234567890123469',
                'balance': Decimal('95000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Lotfi',
                'last_name': 'Mansouri',
                'email': 'lotfi.mansouri@example.com',
                'national_id': '1234567890123470',
                'balance': Decimal('200000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Amina',
                'last_name': 'Rezig',
                'email': 'amina.rezig@example.com',
                'national_id': '1234567890123471',
                'balance': Decimal('130000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Abdelkader',
                'last_name': 'Rahmani',
                'email': 'abdelkader.rahmani@example.com',
                'national_id': '1234567890123472',
                'balance': Decimal('350000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Kawther',
                'last_name': 'Ziani',
                'email': 'kawther.ziani@example.com',
                'national_id': '1234567890123473',
                'balance': Decimal('80000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Reda',
                'last_name': 'Bouzid',
                'email': 'reda.bouzid@example.com',
                'national_id': '1234567890123474',
                'balance': Decimal('160000.00'),
                'password': 'TestPass123!'
            },
            {
                'first_name': 'Ines',
                'last_name': 'Gharbi',
                'email': 'ines.gharbi@example.com',
                'national_id': '1234567890123475',
                'balance': Decimal('140000.00'),
                'password': 'TestPass123!'
            }
        ]
        
        created_profiles = []
        
        for client_data in algerian_clients:
            try:
                # Create client profile
                profile = ClientProfile.objects.create(
                    first_name=client_data['first_name'],
                    last_name=client_data['last_name'],
                    national_id=client_data['national_id'],
                    balance=client_data['balance'],
                    device_fingerprint=f"device_{client_data['national_id'][-4:]}",
                    home_lat=Decimal('36.7538'),  # Algiers coordinates
                    home_lng=Decimal('3.0588'),
                    last_known_lat=Decimal('36.7538'),
                    last_known_lng=Decimal('3.0588'),
                    avg_amount=client_data['balance'] * Decimal('0.1'),  # 10% of balance as avg
                    std_amount=client_data['balance'] * Decimal('0.05')  # 5% of balance as std
                )
                
                # Store profile data for JSON export
                created_profiles.append({
                    'first_name': client_data['first_name'],
                    'last_name': client_data['last_name'],
                    'email': client_data['email'],
                    'national_id': client_data['national_id'],
                    'bank_account_number': profile.bank_account_number,
                    'balance': str(client_data['balance']),
                    'password': client_data['password'],
                    'device_fingerprint': profile.device_fingerprint
                })
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created profile: {profile.full_name} - Account: {profile.bank_account_number} - Balance: {profile.balance} DZD'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating profile for {client_data["first_name"]} {client_data["last_name"]}: {e}')
                )
        
        # Save profiles to JSON file for easy testing
        json_file_path = os.path.join(os.getcwd(), 'setup_profiles.json')
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(created_profiles, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(created_profiles)} Algerian client profiles')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Profile data saved to: {json_file_path}')
        )
        self.stdout.write(
            self.style.WARNING('Note: Users need to register with matching credentials to link to these profiles')
        )
