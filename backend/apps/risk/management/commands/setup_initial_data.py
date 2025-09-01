from django.core.management.base import BaseCommand
from apps.risk.models import Threshold, ClientProfile
from decimal import Decimal

class Command(BaseCommand):
    help = 'Set up initial data for SafeNetAi'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # Create default thresholds
        thresholds_data = [
            ('large_withdrawal', 10000, 'Large withdrawal threshold'),
            ('high_frequency_count', 5, 'High frequency transaction count'),
            ('high_frequency_hours', 1, 'High frequency time window (hours)'),
            ('low_balance', 100, 'Low balance threshold'),
            ('location_anomaly_km', 50, 'Location anomaly threshold (km)'),
            ('location_time_hours', 1, 'Location time window (hours)'),
            ('z_score_threshold', 2.0, 'Z-score threshold for statistical outliers'),
            ('high_risk_threshold', 70, 'High risk threshold for OTP requirement'),
        ]
        
        for key, value, description in thresholds_data:
            threshold, created = Threshold.objects.get_or_create(
                key=key,
                defaults={'value': value, 'description': description}
            )
            if created:
                self.stdout.write(f'Created threshold: {key} = {value}')
            else:
                self.stdout.write(f'Threshold already exists: {key}')
        
        # Create a test client profile
        test_profile, created = ClientProfile.objects.get_or_create(
            national_id='123456789',
            defaults={
                'first_name': 'John',
                'last_name': 'Doe',
                'balance': Decimal('5000.00'),
                'avg_amount': Decimal('500.00'),
                'std_amount': Decimal('200.00'),
                'home_lat': Decimal('40.7128'),
                'home_lng': Decimal('-74.0060'),
                'last_known_lat': Decimal('40.7128'),
                'last_known_lng': Decimal('-74.0060'),
            }
        )
        
        if created:
            self.stdout.write(f'Created test client profile: {test_profile.full_name}')
        else:
            self.stdout.write(f'Test client profile already exists: {test_profile.full_name}')
        
        self.stdout.write(self.style.SUCCESS('Initial data setup completed successfully!'))
