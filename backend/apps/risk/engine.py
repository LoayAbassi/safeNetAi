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
        logger.info(f"Transaction details: Amount={transaction.amount} DZD, Type={transaction.transaction_type}, Client={transaction.client.full_name}")
        
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
            trigger_msg = f"Large {transaction.transaction_type}: {transaction.amount} DZD > {large_withdrawal_threshold} DZD"
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
                trigger_msg = f"Low balance after transaction: {post_balance} DZD < {low_balance_threshold} DZD"
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
        
        # Rule 4: Enhanced Distance-Based Location Rule with Effective Distance Logic
        # Compare current location with BOTH home and last known locations
        # Use the shorter distance (effective distance) to determine if transaction triggers violation
        
        max_distance_threshold = self.thresholds.get('max_distance_km', 50)  # Default 50km
        if (client.home_lat and client.home_lng):
            
            # Get current transaction location from the transaction object
            # Use transaction's stored location if available, otherwise fall back to client's last known
            if hasattr(transaction, 'current_lat') and hasattr(transaction, 'current_lng') and transaction.current_lat and transaction.current_lng:
                current_transaction_lat = float(transaction.current_lat)
                current_transaction_lng = float(transaction.current_lng)
            else:
                # Fallback to client's last known location
                current_transaction_lat = float(client.last_known_lat or client.home_lat)
                current_transaction_lng = float(client.last_known_lng or client.home_lng)
            
            # Calculate distance from home location
            distance_from_home = haversine_distance(
                float(client.home_lat), float(client.home_lng),
                current_transaction_lat, current_transaction_lng
            )
            
            # Calculate distance from last verified location (from previous successful OTP transaction)
            # Get the most recent OTP-verified transaction's location as last known safe location
            distance_from_last_verified = distance_from_home  # Default fallback to home distance
            
            # Find last verified transaction (completed with OTP or low-risk completed)
            last_verified_transaction = Transaction.objects.filter(
                client=client,
                created_at__lt=transaction.created_at,
                status='completed'
            ).order_by('-created_at').first()
            
            if last_verified_transaction and client.last_known_lat and client.last_known_lng:
                # Use the current last_known as the last verified location
                # (this represents the location from the most recent successful transaction)
                distance_from_last_verified = haversine_distance(
                    float(client.last_known_lat), float(client.last_known_lng),
                    current_transaction_lat, current_transaction_lng
                )
            
            # EFFECTIVE DISTANCE LOGIC: Take minimum of both distances
            # This gives users the benefit of the doubt - they're safe if they're close to either location
            effective_distance = min(distance_from_home, distance_from_last_verified)
            
            # Determine which location provided the effective (shorter) distance
            closest_location = "HOME" if distance_from_home <= distance_from_last_verified else "LAST_VERIFIED"
            
            # Enhanced logging showing all three distances with clear formatting
            logger.info(f"🎯 Enhanced Distance-Based Risk Analysis for Transaction {transaction.id}:")
            logger.info(f"  📍 Home location: ({client.home_lat}, {client.home_lng})")
            logger.info(f"  📍 Current transaction location: ({current_transaction_lat}, {current_transaction_lng})")
            if client.last_known_lat and client.last_known_lng:
                logger.info(f"  📍 Last verified location: ({client.last_known_lat}, {client.last_known_lng})")
            logger.info(f"  📏 Distance from home: {distance_from_home:.2f}km")
            logger.info(f"  📏 Distance from last verified: {distance_from_last_verified:.2f}km")
            logger.info(f"  🎯 Effective distance: {effective_distance:.2f}km (minimum = safest path)")
            logger.info(f"  🏆 Closest reference point: {closest_location}")
            logger.info(f"  🚧 Distance threshold: {max_distance_threshold}km")
            
            # Use effective distance for OTP decision
            within_effective_threshold = effective_distance <= max_distance_threshold
            
            if within_effective_threshold:
                logger.info(f"✅ LOCATION APPROVED: Effective distance {effective_distance:.2f}km "
                           f"(closest to {closest_location}) is within {max_distance_threshold}km threshold")
                
                # Log successful validation with detailed information
                log_rule_evaluation(
                    rule_name="Effective Distance Validation - APPROVED",
                    transaction_id=transaction.id,
                    triggered=False,
                    risk_score=risk_score,
                    triggers=[
                        f"✅ Location approved by effective distance: {effective_distance:.2f}km ≤ {max_distance_threshold}km",
                        f"Distance from home: {distance_from_home:.2f}km", 
                        f"Distance from last verified: {distance_from_last_verified:.2f}km",
                        f"Effective distance (minimum): {effective_distance:.2f}km",
                        f"Approved by: {closest_location} location"
                    ]
                )
            else:
                # Effective distance exceeds threshold - trigger OTP
                risk_score += 50  # High risk score for location anomaly
                trigger_msg = f"⚠️ Effective distance violation: {effective_distance:.2f}km > {max_distance_threshold}km threshold"
                triggers.append(trigger_msg)
                logger.warning(f"Rule 4 triggered: {trigger_msg}")
                
                # Detailed logging for OTP requirement
                logger.warning(f"❌ LOCATION VIOLATION: Effective distance {effective_distance:.2f}km exceeds {max_distance_threshold}km threshold")
                logger.warning(f"  📏 Distance from home: {distance_from_home:.2f}km")
                logger.warning(f"  📏 Distance from last verified: {distance_from_last_verified:.2f}km")
                logger.warning(f"  🚫 Both distances exceed threshold - OTP REQUIRED")
                
                log_rule_evaluation(
                    rule_name="Effective Distance Violation - OTP REQUIRED",
                    transaction_id=transaction.id,
                    triggered=True,
                    risk_score=risk_score,
                    triggers=[
                        f"❌ EFFECTIVE DISTANCE VIOLATION: {effective_distance:.2f}km > {max_distance_threshold}km",
                        f"Distance from home: {distance_from_home:.2f}km",
                        f"Distance from last verified: {distance_from_last_verified:.2f}km", 
                        f"Effective distance (minimum): {effective_distance:.2f}km",
                        f"Both distances exceed threshold → OTP REQUIRED"
                    ]
                )
                
                # This rule ALWAYS requires OTP when effective distance is violated
                requires_otp = True
                logger.critical(f"🔐 MANDATORY OTP REQUIRED: Effective distance {effective_distance:.2f}km "
                               f"exceeds {max_distance_threshold}km threshold for transaction {transaction.id}")
        else:
            logger.warning(f"Enhanced distance check skipped: Missing home location data for client {client.id}")
            # Log missing location data with specific details
            missing_fields = []
            if not client.home_lat: missing_fields.append('home_lat')
            if not client.home_lng: missing_fields.append('home_lng') 
            
            log_rule_evaluation(
                rule_name="Effective Distance Check - SKIPPED",
                transaction_id=transaction.id,
                triggered=False,
                risk_score=risk_score,
                triggers=[f"Skipped: Missing home location data - {', '.join(missing_fields)}"]
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
        
        # ENHANCED OTP LOGIC: Effective distance-based mandatory OTP
        # If effective distance rule triggered, OTP is MANDATORY regardless of other thresholds
        high_risk_threshold = self.thresholds.get('high_risk_threshold', 70)
        
        # Check if effective distance violation occurred
        effective_distance_triggered = any('effective distance violation' in trigger.lower() for trigger in triggers)
        
        if effective_distance_triggered:
            requires_otp = True  # Force OTP for effective distance violations
            logger.critical(f"🔐 Effective distance-based OTP enforcement: Transaction {transaction.id} requires mandatory OTP")
        else:
            # Check other conditions for OTP requirement
            requires_otp = risk_score >= high_risk_threshold
            if requires_otp:
                logger.warning(f"High risk score OTP requirement: Transaction {transaction.id} requires OTP (Score: {risk_score})")
        
        # Determine AI decision
        decision = self._get_ai_decision(risk_score, triggers)
        
        logger.info(f"Risk assessment completed: Score={risk_score}, Triggers={len(triggers)}, Requires OTP={requires_otp}, Decision={decision}")
        
        return risk_score, triggers, requires_otp, decision
    
    def calculate_enhanced_location_features(self, transaction):
        """Calculate enhanced location features for ML model with effective distance logic
        
        Returns:
            dict: Contains distance_from_home, distance_from_last_verified, effective_distance
        """
        client = transaction.client
        
        # Default values if location data is missing
        features = {
            'distance_from_home': 0.0,
            'distance_from_last_verified': 0.0, 
            'effective_distance': 0.0,
            'has_location_data': False
        }
        
        if (client.home_lat and client.home_lng):
            
            # Get current transaction location from the transaction object
            if hasattr(transaction, 'current_lat') and hasattr(transaction, 'current_lng') and transaction.current_lat and transaction.current_lng:
                current_transaction_lat = float(transaction.current_lat)
                current_transaction_lng = float(transaction.current_lng)
            else:
                # Fallback to client's last known location
                current_transaction_lat = float(client.last_known_lat or client.home_lat)
                current_transaction_lng = float(client.last_known_lng or client.home_lng)
            
            # Calculate distance from home
            distance_from_home = haversine_distance(
                float(client.home_lat), float(client.home_lng),
                current_transaction_lat, current_transaction_lng
            )
            
            # Calculate distance from last verified location (previous successful transaction)
            distance_from_last_verified = distance_from_home  # Default fallback
            
            # Find last verified transaction
            last_verified_transaction = Transaction.objects.filter(
                client=client,
                created_at__lt=transaction.created_at,
                status='completed'
            ).order_by('-created_at').first()
            
            if last_verified_transaction and client.last_known_lat and client.last_known_lng:
                distance_from_last_verified = haversine_distance(
                    float(client.last_known_lat), float(client.last_known_lng),
                    current_transaction_lat, current_transaction_lng
                )
            
            # Calculate effective distance (minimum of both)
            effective_distance = min(distance_from_home, distance_from_last_verified)
            
            logger.info(f"ML Location features: Home={distance_from_home:.2f}km, "
                       f"LastVerified={distance_from_last_verified:.2f}km, "
                       f"Effective={effective_distance:.2f}km")
            
            features.update({
                'distance_from_home': distance_from_home,
                'distance_from_last_verified': distance_from_last_verified,
                'effective_distance': effective_distance,
                'has_location_data': True
            })
        
        return features

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
