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
        
        # Initialize variables
        risk_score = 0
        triggers = []
        requires_otp = False  # Initialize to False to prevent UnboundLocalError
        
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
        
        # Rule 4: Enhanced Distance-Based Location Rule
        max_distance_threshold = self.thresholds.get('max_distance_km', 50)  # Default 50km
        if (client.home_lat and client.home_lng and 
            client.last_known_lat and client.last_known_lng):
            
            # Calculate distance from home location
            distance_from_home = haversine_distance(
                float(client.home_lat), float(client.home_lng),
                float(client.last_known_lat), float(client.last_known_lng)
            )
            
            # Calculate distance from previous last known location (if different from current)
            distance_from_previous = 0
            previous_transactions = Transaction.objects.filter(
                client=client,
                created_at__lt=transaction.created_at
            ).order_by('-created_at')
            
            if previous_transactions.exists():
                # For this calculation, we'll use the current transaction's location vs stored last_known
                # This represents the distance moved for this transaction
                distance_from_previous = 0  # Will be calculated in transaction view if needed
            
            logger.info(f"Enhanced distance check: "
                       f"Home=({client.home_lat}, {client.home_lng}), "
                       f"Current=({client.last_known_lat}, {client.last_known_lng}), "
                       f"Distance from home={distance_from_home:.2f}km, "
                       f"Threshold={max_distance_threshold}km")
            
            # Check if current location is within threshold of EITHER home OR last known location
            within_home_threshold = distance_from_home <= max_distance_threshold
            
            if within_home_threshold:
                logger.info(f"Location approved: {distance_from_home:.2f}km from home (within {max_distance_threshold}km threshold)")
                # Log which location validated the transaction
                log_rule_evaluation(
                    rule_name="Enhanced Location Validation",
                    transaction_id=transaction.id,
                    triggered=False,
                    risk_score=risk_score,
                    triggers=[f"Location approved: {distance_from_home:.2f}km from home location (within threshold)"]
                )
            else:
                # Distance exceeds threshold - trigger OTP
                risk_score += 50  # High risk score for location anomaly
                trigger_msg = f"Enhanced distance rule: {distance_from_home:.2f}km from home > {max_distance_threshold}km threshold"
                triggers.append(trigger_msg)
                logger.warning(f"Rule 4 triggered: {trigger_msg}")
                
                # Log rule evaluation
                log_rule_evaluation(
                    rule_name="Enhanced Distance from Home/Last Known",
                    transaction_id=transaction.id,
                    triggered=True,
                    risk_score=risk_score,
                    triggers=[trigger_msg]
                )
                
                # This rule ALWAYS requires OTP - don't rely on high_risk_threshold
                requires_otp = True
                logger.critical(f"MANDATORY OTP REQUIRED: Enhanced distance-based fraud detection triggered for transaction {transaction.id}")
        else:
            logger.warning(f"Enhanced distance check skipped: Missing location data for client {client.id}")
            # Log missing location data
            log_rule_evaluation(
                rule_name="Enhanced Distance from Home/Last Known",
                transaction_id=transaction.id,
                triggered=False,
                risk_score=risk_score,
                triggers=["Skipped: Missing location data"]
            )
        
        # Rule 5: Statistical outlier (previously Rule 5)
        if client.avg_amount > 0 and client.std_amount > 0:
            z_score_threshold = self.thresholds.get('z_score_threshold', 2.0)
            z_score = abs((transaction.amount - client.avg_amount) / client.std_amount)
            
            if z_score > z_score_threshold:
                risk_score += 15
                trigger_msg = f"Statistical outlier: z-score {z_score:.2f} > {z_score_threshold}"
                triggers.append(trigger_msg)
                logger.warning(f"Rule 5 triggered: {trigger_msg}")
        
        # Rule 6: Unusual time of day (previously Rule 6)
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
        
        # ENHANCED OTP LOGIC: Distance-based mandatory OTP
        # If distance rule triggered, OTP is MANDATORY regardless of other thresholds
        high_risk_threshold = self.thresholds.get('high_risk_threshold', 70)
        
        # Check if any distance-based trigger exists
        distance_triggered = any('distance exceeded' in trigger.lower() for trigger in triggers)
        
        if distance_triggered:
            requires_otp = True  # Force OTP for distance violations
            logger.critical(f"Distance-based OTP enforcement: Transaction {transaction.id} requires mandatory OTP")
        else:
            # Check other conditions for OTP requirement
            requires_otp = risk_score >= high_risk_threshold
            if requires_otp:
                logger.warning(f"High risk score OTP requirement: Transaction {transaction.id} requires OTP (Score: {risk_score})")
        
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
        """Create a fraud alert for the transaction with logging (prevent duplicates)"""
        from apps.transactions.models import FraudAlert
        
        # Check if fraud alert already exists for this transaction
        existing_alert = FraudAlert.objects.filter(transaction=transaction).first()
        if existing_alert:
            logger.info(f"Fraud alert already exists for transaction {transaction.id}: ID {existing_alert.id}")
            return existing_alert
        
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
