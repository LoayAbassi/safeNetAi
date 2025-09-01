from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.risk.models import ClientProfile
from apps.transactions.models import Transaction
from decimal import Decimal
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generate realistic fake transactions for Algerian client profiles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--transactions-per-client',
            type=int,
            default=15,
            help='Number of transactions to generate per client (default: 15)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Generating fake transactions...'))
        
        transactions_per_client = options['transactions_per_client']
        
        # Get all client profiles
        clients = ClientProfile.objects.all()
        
        if not clients.exists():
            self.stdout.write(self.style.ERROR('No client profiles found. Please run setup_algerian_profiles first.'))
            return
        
        total_transactions = 0
        
        for client in clients:
            self.stdout.write(f'Generating transactions for {client.full_name}...')
            
            # Generate transactions for this client
            client_transactions = self._generate_client_transactions(client, transactions_per_client)
            total_transactions += len(client_transactions)
            
            self.stdout.write(
                self.style.SUCCESS(f'Generated {len(client_transactions)} transactions for {client.full_name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated {total_transactions} transactions across {clients.count()} clients')
        )
        
        # Update client statistics for ML model
        self.stdout.write('Updating client statistics...')
        self._update_client_statistics()
        
        self.stdout.write(
            self.style.SUCCESS('Transaction generation completed!')
        )

    def _generate_client_transactions(self, client, num_transactions):
        """Generate realistic transactions for a specific client"""
        transactions = []
        
        # Get other clients for transfers
        other_clients = list(ClientProfile.objects.exclude(id=client.id))
        
        # Transaction types with realistic probabilities
        transaction_types = [
            ('deposit', 0.3),      # 30% deposits
            ('withdraw', 0.2),     # 20% withdrawals
            ('transfer', 0.5),     # 50% transfers
        ]
        
        # Generate transactions over the last 30 days
        base_date = timezone.now() - timedelta(days=30)
        
        for i in range(num_transactions):
            # Random date within last 30 days
            transaction_date = base_date + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Choose transaction type based on probabilities
            transaction_type = random.choices(
                [t[0] for t in transaction_types],
                weights=[t[1] for t in transaction_types]
            )[0]
            
            # Generate realistic amount based on transaction type and client balance
            amount = self._generate_realistic_amount(client, transaction_type)
            
            # Generate transaction data
            transaction_data = {
                'client': client,
                'amount': amount,
                'transaction_type': transaction_type,
                'status': 'completed',
                'device_fingerprint': client.device_fingerprint,
                'location_lat': client.last_known_lat,
                'location_lng': client.last_known_lng,
                'created_at': transaction_date,
            }
            
            # Add transfer-specific data
            if transaction_type == 'transfer' and other_clients:
                recipient = random.choice(other_clients)
                transaction_data['to_account_number'] = recipient.bank_account_number
            
            # Create transaction
            transaction = Transaction.objects.create(**transaction_data)
            transactions.append(transaction)
            
            # Update client balance (simulate the transaction effect)
            if transaction_type == 'deposit':
                client.balance += amount
            elif transaction_type in ['withdraw', 'transfer']:
                client.balance -= amount
                
                # For transfers, also update recipient balance
                if transaction_type == 'transfer' and other_clients:
                    try:
                        recipient = ClientProfile.objects.get(
                            bank_account_number=transaction_data['to_account_number']
                        )
                        recipient.balance += amount
                        recipient.save()
                    except ClientProfile.DoesNotExist:
                        pass
            
            client.save()
        
        return transactions

    def _generate_realistic_amount(self, client, transaction_type):
        """Generate realistic transaction amounts based on client balance and transaction type"""
        balance = float(client.balance)
        
        if transaction_type == 'deposit':
            # Deposits: 5% to 50% of balance, or 1000-50000 DZD
            min_amount = min(balance * 0.05, 1000)
            max_amount = min(balance * 0.5, 50000)
            
        elif transaction_type == 'withdraw':
            # Withdrawals: 5% to 30% of balance, but never more than available balance
            min_amount = min(balance * 0.05, 1000)
            max_amount = min(balance * 0.3, balance * 0.8)  # Leave some balance
            
        else:  # transfer
            # Transfers: 10% to 40% of balance, but never more than available balance
            min_amount = min(balance * 0.1, 2000)
            max_amount = min(balance * 0.4, balance * 0.7)  # Leave some balance
        
        # Generate amount with some randomness
        amount = random.uniform(min_amount, max_amount)
        
        # Round to nearest 100 DZD for realism
        amount = round(amount / 100) * 100
        
        # Ensure minimum amount
        amount = max(amount, 500)
        
        return Decimal(str(amount))

    def _update_client_statistics(self):
        """Update client statistics for ML model training"""
        from apps.risk.ml import FraudMLModel
        
        ml_model = FraudMLModel()
        ml_model.update_client_statistics()
        
        self.stdout.write(
            self.style.SUCCESS('Client statistics updated for ML model training')
        )
