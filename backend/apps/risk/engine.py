import math
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from .models import ClientProfile, Threshold, Rule
from apps.transactions.models import Transaction
from apps.utils.logger import get_rules_logger, log_rule_evaluation, log_system_event

# Set up logger
logger = get_rules_logger()

def haversine_distance(lat1, lng1, lat2, lng2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    if not all([lat1, lng1, lat2, lng2]):
        return 0
    
    # Convert decimal degrees to radians
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r

class RiskEngine:
    def __init__(self):
        self.thresholds = self._load_thresholds()
        self.rules = self._load_rules()
        logger.info(f"RiskEngine initialized with {len(self.thresholds)} thresholds and {len(self.rules)} rules")
        log_system_event(
            "RiskEngine initialized",
            "risk_engine",
            "INFO",
            {"thresholds_count": len(self.thresholds), "rules_count": len(self.rules)}
        )
    
    def _load_thresholds(self):
        """Load all thresholds from database"""
        thresholds = {}
        for threshold in Threshold.objects.all():
            thresholds[threshold.key] = threshold.value
        return thresholds
    
    def _load_rules(self):
        """Load all enabled rules from database"""
        return Rule.objects.filter(enabled=True)
    
    def calculate_risk_score(self, transaction):
        """
        Calculate risk score for a transaction with comprehensive logging
        Returns: (risk_score, triggers, requires_otp, decision)
        """
        logger.info(f"Starting risk assessment for transaction {transaction.id}")
        logger.info(f"Transaction details: Amount=${transaction.amount}, Type={transaction.transaction_type}, Client={transaction.client.full_name}")
        
        risk_score = 0
        triggers = []
        
        # Get client profile
        client = transaction.client
        
        # Rule 1: Large withdrawal/transfer
        large_withdrawal_threshold = self.thresholds.get('large_withdrawal', 10000)
        if (transaction.transaction_type in ['withdraw', 'transfer'] and 
            transaction.amount > large_withdrawal_threshold):
            risk_score += 30
            trigger_msg = f"Large {transaction.transaction_type}: ${transaction.amount} > ${large_withdrawal_threshold}"
            triggers.append(trigger_msg)
            logger.warning(f"Rule 1 triggered: {trigger_msg}")
            
            # Log rule evaluation
            log_rule_evaluation(
                rule_name="Large Withdrawal/Transfer",
                transaction_id=transaction.id,
                triggered=True,
                risk_score=risk_score,
                triggers=[trigger_msg]
            )
        
        # Rule 2: High frequency transactions
        high_freq_threshold = self.thresholds.get('high_frequency_count', 5)
        high_freq_hours = self.thresholds.get('high_frequency_hours', 1)
        recent_transactions = Transaction.objects.filter(
            client=client,
            created_at__gte=timezone.now() - timedelta(hours=high_freq_hours)
        ).count()
        
        if recent_transactions > high_freq_threshold:
            risk_score += 25
            trigger_msg = f"High frequency: {recent_transactions} transactions in {high_freq_hours} hour(s)"
            triggers.append(trigger_msg)
            logger.warning(f"Rule 2 triggered: {trigger_msg}")
            
            # Log rule evaluation
            log_rule_evaluation(
                rule_name="High Frequency Transactions",
                transaction_id=transaction.id,
                triggered=True,
                risk_score=risk_score,
                triggers=[trigger_msg]
            )
        
        # Rule 3: Low balance after withdrawal
        low_balance_threshold = self.thresholds.get('low_balance', 100)
        if transaction.transaction_type in ['withdraw', 'transfer']:
            post_balance = client.balance - transaction.amount
            if post_balance < low_balance_threshold:
                risk_score += 20
                trigger_msg = f"Low balance after transaction: ${post_balance} < ${low_balance_threshold}"
                triggers.append(trigger_msg)
                logger.warning(f"Rule 3 triggered: {trigger_msg}")
                
                # Log rule evaluation
                log_rule_evaluation(
                    rule_name="Low Balance After Transaction",
                    transaction_id=transaction.id,
                    triggered=True,
                    risk_score=risk_score,
                    triggers=[trigger_msg]
                )
        
        # Rule 4: Location anomaly (temporarily disabled - location fields removed)
        # TODO: Re-implement when location tracking is added back
        # Currently skipped due to removed location_lat/lng fields
        
        # Rule 5: Statistical outlier
        if client.avg_amount > 0 and client.std_amount > 0:
            z_score_threshold = self.thresholds.get('z_score_threshold', 2.0)
            z_score = abs((transaction.amount - client.avg_amount) / client.std_amount)
            
            if z_score > z_score_threshold:
                risk_score += 15
                trigger_msg = f"Statistical outlier: z-score {z_score:.2f} > {z_score_threshold}"
                triggers.append(trigger_msg)
                logger.warning(f"Rule 5 triggered: {trigger_msg}")
        
        # Rule 6: Unusual time of day
        hour = transaction.created_at.hour
        unusual_hours = [23, 0, 1, 2, 3, 4, 5]  # Late night/early morning
        if hour in unusual_hours:
            risk_score += 10
            trigger_msg = f"Unusual time: {hour}:00"
            triggers.append(trigger_msg)
            logger.info(f"Rule 6 triggered: {trigger_msg}")
        
        # Rule 7: Device fingerprint anomaly (temporarily disabled - device_fingerprint field removed)
        # TODO: Re-implement when device fingerprinting is added back
        # Currently skipped due to removed device_fingerprint field
        
        # Determine if OTP is required
        high_risk_threshold = self.thresholds.get('high_risk_threshold', 70)
        requires_otp = risk_score >= high_risk_threshold
        
        # Determine AI decision
        decision = self._get_ai_decision(risk_score, triggers)
        
        logger.info(f"Risk assessment completed: Score={risk_score}, Triggers={len(triggers)}, Requires OTP={requires_otp}, Decision={decision}")
        
        return risk_score, triggers, requires_otp, decision
    
    def _get_ai_decision(self, risk_score, triggers):
        """Get AI decision based on risk score and triggers"""
        if risk_score >= 80:
            return "Block"
        elif risk_score >= 60:
            return "Flag for Review"
        elif risk_score >= 40:
            return "Monitor"
        else:
            return "Approve"
    
    def get_risk_level(self, risk_score):
        """Convert risk score to risk level"""
        if risk_score >= 70:
            return 'High'
        elif risk_score >= 40:
            return 'Medium'
        else:
            return 'Low'
    
    def create_fraud_alert(self, transaction, risk_score, triggers):
        """Create a fraud alert for the transaction with logging"""
        from apps.transactions.models import FraudAlert
        
        level = self.get_risk_level(risk_score)
        message = f"Transaction flagged with {level} risk (Score: {risk_score}). Triggers: {', '.join(triggers)}"
        
        logger.info(f"Creating fraud alert for transaction {transaction.id}: {level} risk, score {risk_score}")
        
        fraud_alert = FraudAlert.objects.create(
            transaction=transaction,
            risk_score=risk_score,
            level=level,
            triggers=triggers
        )
        
        logger.info(f"Fraud alert created: ID {fraud_alert.id}")
        return fraud_alert
    
    def get_risk_summary(self, transaction):
        """Get comprehensive risk summary for a transaction"""
        risk_score, triggers, requires_otp, decision = self.calculate_risk_score(transaction)
        
        return {
            'transaction_id': transaction.id,
            'risk_score': risk_score,
            'risk_level': self.get_risk_level(risk_score),
            'triggers': triggers,
            'requires_otp': requires_otp,
            'ai_decision': decision,
            'assessment_time': timezone.now(),
            'client_name': transaction.client.full_name,
            'amount': transaction.amount,
            'transaction_type': transaction.transaction_type
        }
