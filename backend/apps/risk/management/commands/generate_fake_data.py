"""
Django management command to generate fake data for SafeNetAi
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import random
from datetime import timedelta

from apps.users.models import EmailOTP
from apps.risk.models import ClientProfile, Threshold, Rule, generate_random_8digit
from apps.transactions.models import Transaction, FraudAlert, TransactionOTP
from apps.utils.logger import get_system_logger, log_system_event

User = get_user_model()
logger = get_system_logger()

class Command(BaseCommand):
    help = 'Generate fake data for SafeNetAi testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=20,
            help='Number of fake users to create'
        )
        parser.add_argument(
            '--transactions',
            type=int,
            default=100,
            help='Number of fake transactions to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting fake data generation...'))
        
        if options['clear']:
            self.clear_existing_data()
        
        try:
            with transaction.atomic():
                # Generate admin user
                admin_user = self.create_admin_user()
                
                # Generate Algerian profiles first (as requested)
                algerian_profiles_count = self.create_algerian_profiles()
                
                # Generate regular users
                users = self.create_fake_users(options['users'])
                
                # Generate additional client profiles
                client_profiles = self.create_client_profiles(users)
                
                # Combine all profiles for transaction generation
                all_profiles = list(ClientProfile.objects.all())
                
                # Generate thresholds and rules
                self.create_thresholds_and_rules()
                
                # Generate transactions using all profiles
                transactions = self.create_fake_transactions(all_profiles, options['transactions'])
                
                # Generate fraud alerts
                self.create_fake_fraud_alerts(transactions)
                
                # Generate some OTPs
                self.create_fake_otps(users)
                
                # Generate transaction OTPs
                self.create_fake_transaction_otps(transactions)
                
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully generated fake data:\n'
                    f'- 1 Admin user\n'
                    f'- {len(users)} Regular users\n'
                    f'- {algerian_profiles_count} Algerian client profiles\n'
                    f'- {len(client_profiles)} Additional client profiles\n'
                    f'- {len(transactions)} Transactions\n'
                    f'- Multiple fraud alerts and OTPs'
                )
            )
            
            # Log the fake data generation
            log_system_event(
                "Fake data generation completed",
                "management",
                "INFO",
                {
                    "users_created": len(users) + 1,  # +1 for admin
                    "algerian_profiles_created": algerian_profiles_count,
                    "additional_profiles_created": len(client_profiles),
                    "transactions_created": len(transactions)
                }
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating fake data: {e}'))
            logger.error(f"Error generating fake data: {e}")

    def clear_existing_data(self):
        """Clear existing data"""
        self.stdout.write('Clearing existing data...')
        
        TransactionOTP.objects.all().delete()
        FraudAlert.objects.all().delete()
        Transaction.objects.all().delete()
        ClientProfile.objects.all().delete()
        EmailOTP.objects.all().delete()
        Rule.objects.all().delete()
        Threshold.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(self.style.SUCCESS('Existing data cleared'))

    def create_admin_user(self):
        """Create admin user"""
        admin_user, created = User.objects.get_or_create(
            email='admin@safenetai.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'is_email_verified': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Admin user created: admin@safenetai.com / admin123')
        
        return admin_user

    def create_fake_users(self, count):
        """Create fake users"""
        users = []
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa', 'James', 'Maria']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{first_name.lower()}.{last_name.lower()}{i+1}@example.com"
            
            user = User.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_email_verified=True
            )
            user.set_password('password123')
            user.save()
            users.append(user)
        
        self.stdout.write(f'Created {count} fake users')
        return users

    def create_client_profiles(self, users):
        """Create client profiles for users"""
        profiles = []
        cities = ['Algiers', 'Oran', 'Constantine', 'Annaba', 'Blida', 'Batna', 'Djelfa', 'Setif', 'Sidi Bel Abbes', 'Biskra']
        
        for user in users:
            profile = ClientProfile.objects.create(
                user=user,
                first_name=user.first_name,
                last_name=user.last_name,
                national_id=f"AL{random.randint(100000000000, 999999999999)}",
                phone_number=f"+213{random.randint(500000000, 999999999)}",
                address=f"{random.randint(1, 999)} {random.choice(['Street', 'Avenue', 'Boulevard'])}",
                city=random.choice(cities),
                balance=Decimal(random.randint(1000, 50000))
            )
            profiles.append(profile)
        
        self.stdout.write(f'Created {len(profiles)} client profiles')
        return profiles

    def create_thresholds_and_rules(self):
        """Create thresholds and rules"""
        # Create thresholds
        thresholds_data = [
            ('large_amount', 10000),
            ('high_frequency_count', 5),
            ('high_frequency_hours', 2),
            ('low_balance_threshold', 1000),
            ('unusual_time_start', 23),
            ('unusual_time_end', 6),
        ]
        
        for name, value in thresholds_data:
            Threshold.objects.get_or_create(
                key=name,
                defaults={'value': value}
            )
        
        # Create rules
        rules_data = [
            ('Large Withdrawal/Transfer', 'Triggers when transaction amount exceeds threshold'),
            ('High Frequency Transactions', 'Triggers when multiple transactions occur in short time'),
            ('Low Balance After Withdrawal', 'Triggers when balance falls below threshold after withdrawal'),
            ('Unusual Time Transaction', 'Triggers when transaction occurs during unusual hours'),
        ]
        
        for name, description in rules_data:
            Rule.objects.get_or_create(
                key=name.lower().replace(' ', '_'),
                defaults={'description': description, 'enabled': True}
            )
        
        self.stdout.write('Created thresholds and rules')

    def create_fake_transactions(self, client_profiles, count):
        """Create fake transactions"""
        transactions = []
        transaction_types = ['deposit', 'withdraw', 'transfer']
        
        for i in range(count):
            client_profile = random.choice(client_profiles)
            transaction_type = random.choice(transaction_types)
            
            # Generate realistic amounts based on transaction type
            if transaction_type == 'deposit':
                amount = Decimal(random.randint(100, 5000))
            elif transaction_type == 'withdraw':
                max_withdraw = min(2000, float(client_profile.balance))
                amount = Decimal(random.randint(50, int(max_withdraw)))
            else:  # transfer
                max_transfer = min(3000, float(client_profile.balance))
                amount = Decimal(random.randint(100, int(max_transfer)))
            
            # Generate risk score (some transactions will be high risk)
            risk_score = random.randint(0, 100)
            
            # Determine status based on risk score
            if risk_score >= 70:
                status = 'pending'
            elif risk_score >= 40:
                status = 'completed'
            else:
                status = 'completed'
            
            # Create transaction
            transaction = Transaction.objects.create(
                client=client_profile,
                transaction_type=transaction_type,
                amount=amount,
                to_account_number=f"AL{random.randint(10000000000000000000, 99999999999999999999)}" if transaction_type == 'transfer' else None,
                description=f"Fake {transaction_type} transaction #{i+1}",
                status=status,
                risk_score=risk_score,
                created_at=timezone.now() - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
            )
            transactions.append(transaction)
        
        self.stdout.write(f'Created {len(transactions)} fake transactions')
        return transactions

    def create_fake_fraud_alerts(self, transactions):
        """Create fake fraud alerts for high-risk transactions"""
        alerts = []
        levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        triggers_list = [
            ['Large amount', 'Unusual time'],
            ['High frequency', 'Multiple transactions'],
            ['Low balance', 'Large withdrawal'],
            ['Unusual location', 'New device'],
            ['Suspicious pattern', 'Risk score high']
        ]
        
        # Create alerts for high-risk transactions
        high_risk_transactions = [t for t in transactions if t.risk_score >= 40]
        
        for transaction in high_risk_transactions:
            level = 'HIGH' if transaction.risk_score >= 70 else 'MEDIUM'
            triggers = random.choice(triggers_list)
            
            alert = FraudAlert.objects.create(
                transaction=transaction,
                level=level,
                risk_score=transaction.risk_score,
                triggers=triggers,
                status='Active' if transaction.status == 'pending' else 'Reviewed'
            )
            alerts.append(alert)
        
        self.stdout.write(f'Created {len(alerts)} fake fraud alerts')
        return alerts

    def create_fake_otps(self, users):
        """Create fake email OTPs"""
        otps = []
        
        for user in random.sample(users, min(5, len(users))):
            otp = EmailOTP.objects.create(
                user=user,
                otp=str(random.randint(100000, 999999)),
                expires_at=timezone.now() + timedelta(hours=1),
                used=random.choice([True, False])
            )
            otps.append(otp)
        
        self.stdout.write(f'Created {len(otps)} fake email OTPs')
        return otps

    def create_fake_transaction_otps(self, transactions):
        """Create fake transaction OTPs"""
        otps = []
        
        # Create OTPs for pending transactions
        pending_transactions = [t for t in transactions if t.status == 'pending']
        
        for transaction in pending_transactions:
            otp = TransactionOTP.objects.create(
                transaction=transaction,
                user=transaction.client.user,
                otp=str(random.randint(100000, 999999)),
                expires_at=timezone.now() + timedelta(minutes=10),
                used=random.choice([True, False])
            )
            otps.append(otp)
        
        self.stdout.write(f'Created {len(otps)} fake transaction OTPs')
        return otps

    def create_algerian_profiles(self):
        """Create the 30 specific Algerian profiles as requested"""
        logger.info("Creating 30 specific Algerian client profiles...")
        
        # Specific Algerian profiles as requested
        algerian_profiles = [
            ("Amine", "Bensalem", "amine.bensalem@example.dz", "+213612345678"),
            ("Amina", "Cherif", "amina.cherif@example.dz", "+213623456789"),
            ("Karim", "Haddad", "karim.haddad@example.dz", "+213634567890"),
            ("Samira", "Mecheri", "samira.mecheri@example.dz", "+213645678901"),
            ("Sofiane", "Rahmani", "sofiane.rahmani@example.dz", "+213656789012"),
            ("Nassima", "Bekhti", "nassima.bekhti@example.dz", "+213667890123"),
            ("Yacine", "Belkacem", "yacine.belkacem@example.dz", "+213678901234"),
            ("Naoual", "Boudiaf", "naoual.boudiaf@example.dz", "+213689012345"),
            ("Rachid", "Ferhat", "rachid.ferhat@example.dz", "+213690123456"),
            ("Lila", "Haddouch", "lila.haddouch@example.dz", "+213601234567"),
            ("Nabil", "Slimani", "nabil.slimani@example.dz", "+213612345679"),
            ("Souad", "Zerguine", "souad.zerguine@example.dz", "+213623456780"),
            ("Mourad", "Djellal", "mourad.djellal@example.dz", "+213634567891"),
            ("Leila", "Chouikh", "leila.chouikh@example.dz", "+213645678902"),
            ("Hakim", "Benyahia", "hakim.benyahia@example.dz", "+213656789013"),
            ("Fatiha", "Guemari", "fatiha.guemari@example.dz", "+213667890124"),
            ("Mehdi", "Kaci", "mehdi.kaci@example.dz", "+213678901235"),
            ("Imene", "Touati", "imene.touati@example.dz", "+213689012346"),
            ("Zaki", "Benrabah", "zaki.benrabah@example.dz", "+213690123457"),
            ("Kahina", "Saadi", "kahina.saadi@example.dz", "+213601234568"),
            ("Lotfi", "Cherfaoui", "lotfi.cherfaoui@example.dz", "+213612345670"),
            ("Hanane", "Meziane", "hanane.meziane@example.dz", "+213623456781"),
            ("Walid", "Ferhani", "walid.ferhani@example.dz", "+213634567892"),
            ("Assia", "Boukercha", "assia.boukercha@example.dz", "+213645678903"),
            ("Adel", "Djamai", "adel.djamai@example.dz", "+213656789014"),
            ("Naima", "Bouras", "naima.bouras@example.dz", "+213667890125"),
            ("Hocine", "Khoda", "hocine.khodja@example.dz", "+213678901236"),
            ("Meriem", "Ziani", "meriem.ziani@example.dz", "+213689012347"),
            ("Farid", "Amrani", "farid.amrani@example.dz", "+213690123458"),
            ("Salima", "Haddadi", "salima.haddadi@example.dz", "+213601234569"),
        ]
        
        algerian_cities = [
            "Algiers", "Oran", "Constantine", "Annaba", "Batna", "Blida", "Setif", 
            "Chlef", "Djelfa", "Sidi Bel Abbes", "Biskra", "Tebessa", "El Oued", 
            "Skikda", "Tiaret", "Bejaia", "Tlemcen", "Ouargla", "Mostaganem", "El Eulma"
        ]
        
        # Pre-define street names to avoid f-string syntax issues
        street_names = [
            "de la Paix", "des Martyrs", "de l'Indépendance", 
            "de la Révolution", "du 1er Novembre"
        ]
        
        profiles_created = 0
        
        for first_name, last_name, email, phone in algerian_profiles:
            try:
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    logger.info(f"User {email} already exists, skipping...")
                    continue
                
                # Generate a unique national ID
                national_id = f"{random.randint(100000000, 999999999)}"
                
                # Create user account
                user = User.objects.create_user(
                    email=email,
                    password='testpass123',
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=False,
                    is_active=True
                )
                
                # Create client profile
                profile = ClientProfile.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    national_id=national_id,
                    phone_number=phone,
                    address=f"{random.randint(1, 999)} Rue {random.choice(street_names)}, {random.choice(algerian_cities)}",
                    city=random.choice(algerian_cities),
                    bank_account_number=generate_random_8digit(),
                    balance=Decimal(random.uniform(1000, 50000)).quantize(Decimal('0.01'))
                )
                
                profiles_created += 1
                logger.info(f"Created profile: {first_name} {last_name} ({email})")
                
            except Exception as e:
                logger.error(f"Error creating profile for {first_name} {last_name}: {e}")
        
        logger.info(f"Successfully created {profiles_created} Algerian client profiles")
        return profiles_created
