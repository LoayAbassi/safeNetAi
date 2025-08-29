from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import ClientProfile
from apps.risk.models import Threshold, Rule

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up initial data for SafeNetAi'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@safenetai.com',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        else:
            self.stdout.write('Admin user already exists')
        
        # Create sample client profiles
        sample_clients = [
            {
                'full_name': 'John Doe',
                'national_id': '123456789',
                'bank_account_number': '12345678',
                'balance': 5000.00,
                'risk_score': 0
            },
            {
                'full_name': 'Jane Smith',
                'national_id': '987654321',
                'bank_account_number': '87654321',
                'balance': 15000.00,
                'risk_score': 0
            },
            {
                'full_name': 'Bob Johnson',
                'national_id': '456789123',
                'bank_account_number': '45678912',
                'balance': 2500.00,
                'risk_score': 0
            }
        ]
        
        for client_data in sample_clients:
            client, created = ClientProfile.objects.get_or_create(
                national_id=client_data['national_id'],
                defaults=client_data
            )
            if created:
                self.stdout.write(f"Created client profile for {client.full_name}")
            else:
                self.stdout.write(f"Client profile for {client.full_name} already exists")
        
        # Create default thresholds
        default_thresholds = [
            {
                'key': 'LARGE_WITHDRAWAL_AMOUNT',
                'value': 10000.0,
                'description': 'Amount threshold for large withdrawals'
            },
            {
                'key': 'MAX_TRANSACTIONS_PER_HOUR',
                'value': 5.0,
                'description': 'Maximum number of transactions per hour'
            },
            {
                'key': 'LOW_BALANCE_THRESHOLD',
                'value': 100.0,
                'description': 'Minimum balance threshold after withdrawal'
            },
            {
                'key': 'AVERAGE_TRANSACTION_AMOUNT',
                'value': 1000.0,
                'description': 'Average transaction amount for statistical analysis'
            },
            {
                'key': 'TRANSACTION_STD_DEV',
                'value': 500.0,
                'description': 'Standard deviation for transaction amounts'
            }
        ]
        
        for threshold_data in default_thresholds:
            threshold, created = Threshold.objects.get_or_create(
                key=threshold_data['key'],
                defaults=threshold_data
            )
            if created:
                self.stdout.write(f"Created threshold: {threshold.key}")
            else:
                self.stdout.write(f"Threshold {threshold.key} already exists")
        
        # Create default rules
        default_rules = [
            {
                'key': 'large_withdrawal_rule',
                'description': 'Flag large withdrawals as potentially risky',
                'enabled': True,
                'params_json': {'threshold': 10000}
            },
            {
                'key': 'high_frequency_rule',
                'description': 'Flag high frequency transactions',
                'enabled': True,
                'params_json': {'max_per_hour': 5}
            },
            {
                'key': 'low_balance_rule',
                'description': 'Flag transactions that leave very low balance',
                'enabled': True,
                'params_json': {'min_balance': 100}
            }
        ]
        
        for rule_data in default_rules:
            rule, created = Rule.objects.get_or_create(
                key=rule_data['key'],
                defaults=rule_data
            )
            if created:
                self.stdout.write(f"Created rule: {rule.key}")
            else:
                self.stdout.write(f"Rule {rule.key} already exists")
        
        self.stdout.write(self.style.SUCCESS('Initial data setup completed successfully!'))
