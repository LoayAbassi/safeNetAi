from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from apps.transactions.models import Transaction, FraudAlert
from apps.risk.models import Threshold, Rule

class FraudDetectionEngine:
    """
    Engine for detecting fraudulent transactions based on configurable rules
    """
    
    def __init__(self):
        self.thresholds = self._load_thresholds()
        self.rules = self._load_rules()
    
    def _load_thresholds(self):
        """Load all thresholds from database"""
        thresholds = {}
        for threshold in Threshold.objects.all():
            thresholds[threshold.key] = threshold.value
        return thresholds
    
    def _load_rules(self):
        """Load all enabled rules from database"""
        return Rule.objects.filter(enabled=True)
    
    def detect_fraud(self, transaction):
        """
        Analyze a transaction for potential fraud
        Returns: (risk_level, message, risk_score)
        """
        risk_score = 0
        triggered_rules = []
        
        # Rule 1: Large withdrawal amount
        if transaction.transaction_type == 'withdraw':
            large_withdrawal_threshold = self.thresholds.get('LARGE_WITHDRAWAL_AMOUNT', 10000)
            if transaction.amount > large_withdrawal_threshold:
                risk_score += 30
                triggered_rules.append(f"Large withdrawal: {transaction.amount} > {large_withdrawal_threshold}")
        
        # Rule 2: Multiple transactions in short time
        recent_transactions = Transaction.objects.filter(
            client=transaction.client,
            timestamp__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        max_transactions_per_hour = self.thresholds.get('MAX_TRANSACTIONS_PER_HOUR', 5)
        if recent_transactions > max_transactions_per_hour:
            risk_score += 25
            triggered_rules.append(f"High transaction frequency: {recent_transactions} in last hour")
        
        # Rule 3: Low balance after withdrawal
        if transaction.transaction_type == 'withdraw':
            low_balance_threshold = self.thresholds.get('LOW_BALANCE_THRESHOLD', 100)
            remaining_balance = transaction.client.balance - transaction.amount
            if remaining_balance < low_balance_threshold:
                risk_score += 20
                triggered_rules.append(f"Low balance after withdrawal: {remaining_balance} < {low_balance_threshold}")
        
        # Rule 4: Unusual transaction amount (statistical outlier)
        avg_amount = self.thresholds.get('AVERAGE_TRANSACTION_AMOUNT', 1000)
        std_amount = self.thresholds.get('TRANSACTION_STD_DEV', 500)
        z_score = abs(transaction.amount - avg_amount) / std_amount if std_amount > 0 else 0
        
        if z_score > 2.5:  # More than 2.5 standard deviations
            risk_score += 15
            triggered_rules.append(f"Unusual amount: z-score = {z_score:.2f}")
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = 'High'
        elif risk_score >= 40:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        # Create message
        if triggered_rules:
            message = f"Fraud risk detected. Score: {risk_score}. Triggers: {'; '.join(triggered_rules)}"
        else:
            message = f"Transaction appears normal. Risk score: {risk_score}"
        
        return risk_level, message, risk_score
    
    def create_fraud_alert(self, transaction, risk_level, message):
        """Create a fraud alert for the transaction"""
        return FraudAlert.objects.create(
            transaction=transaction,
            risk_level=risk_level,
            message=message
        )
    
    def should_block_transaction(self, risk_level):
        """Determine if transaction should be blocked based on risk level"""
        return risk_level == 'High'
