import os
import time
import joblib
import numpy as np
import pandas as pd
from django.conf import settings
from django.db.models import Avg, StdDev
from apps.transactions.models import Transaction
from apps.risk.models import ClientProfile
from apps.utils.logger import get_ai_logger, log_prediction, log_system_event

# Set up logger
logger = get_ai_logger()

class FraudMLModel:
    def __init__(self):
        self.model = None
        self.model_path = os.path.join(settings.BASE_DIR, 'models', 'fraud_isolation.joblib')
        self.scaler = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model from disk with logging"""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                logger.info(f"ML model loaded successfully from {self.model_path}")
                log_system_event(
                    "ML model loaded successfully",
                    "fraud_ml_model",
                    "INFO",
                    {"model_path": self.model_path}
                )
                return True
            else:
                logger.warning(f"ML model file not found at {self.model_path}")
                log_system_event(
                    "ML model file not found",
                    "fraud_ml_model",
                    "WARNING",
                    {"model_path": self.model_path}
                )
        except Exception as e:
            logger.error(f"Error loading ML model: {e}")
            log_system_event(
                "Error loading ML model",
                "fraud_ml_model",
                "ERROR",
                {"model_path": self.model_path, "error": str(e)}
            )
        return False
    
    def save_model(self):
        """Save the trained model to disk with logging"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            logger.info(f"ML model saved successfully to {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving ML model: {e}")
            return False
    
    def prepare_features(self, transaction):
        """Prepare enhanced features for a single transaction with effective distance logic"""
        try:
            client = transaction.client
            
            logger.info(f"Preparing enhanced features for transaction {transaction.id}")
            
            # Import here to avoid circular imports
            from apps.risk.engine import RiskEngine
            
            # Get enhanced location features
            risk_engine = RiskEngine()
            location_features = risk_engine.calculate_enhanced_location_features(transaction)
            
            # Enhanced feature set with 9 features including effective distance
            features = [
                float(transaction.amount),                              # 0: Transaction amount
                float(client.balance),                                  # 1: Client balance
                2 if transaction.transaction_type == 'transfer' else 1, # 2: Transaction type (transfer=2, withdraw=1)
                transaction.created_at.hour,                           # 3: Hour of day
                transaction.created_at.weekday(),                      # 4: Day of week
                location_features['distance_from_home'],               # 5: Distance from home
                location_features['distance_from_last_known'],         # 6: Distance from last known
                location_features['effective_distance'],               # 7: Effective distance (min of above)
                float(location_features['has_location_data']),         # 8: Location data availability flag
            ]
            
            feature_array = np.array(features).reshape(1, -1)
            
            logger.info(f"Enhanced ML features prepared: {len(features)} features")
            logger.info(f"Location intelligence - Distance from home: {location_features['distance_from_home']:.2f}km, "
                       f"Distance from last known: {location_features['distance_from_last_known']:.2f}km, "
                       f"Effective distance: {location_features['effective_distance']:.2f}km")
            
            return feature_array
            
        except Exception as e:
            logger.error(f"Error preparing enhanced features for transaction {transaction.id}: {e}")
            # Return default features (9 features with safe defaults)
            return np.array([[0, 0, 2, 0, 0, 0, 0, 0, 0]])
    
    def train(self):
        """Train the fraud detection model with comprehensive logging"""
        try:
            from sklearn.ensemble import IsolationForest
            from sklearn.preprocessing import StandardScaler
            
            logger.info("Starting ML model training...")
            
            # Get all transactions with sufficient data
            transactions = Transaction.objects.select_related('client').all()
            
            if len(transactions) < 10:
                logger.warning(f"Insufficient data for training. Need at least 10 transactions, got {len(transactions)}")
                return False
            
            logger.info(f"Training with {len(transactions)} transactions")
            
            # Prepare features
            features_list = []
            for transaction in transactions:
                features = self.prepare_features(transaction)
                features_list.append(features.flatten())
            
            X = np.array(features_list)
            logger.info(f"Feature matrix shape: {X.shape}")
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            logger.info("Features scaled successfully")
            
            # Train Isolation Forest
            self.model = IsolationForest(
                contamination=0.1,  # Assume 10% of transactions are anomalous
                random_state=42,
                n_estimators=100,
                max_samples='auto'
            )
            
            self.model.fit(X_scaled)
            logger.info("Isolation Forest model trained successfully")
            
            # Evaluate model performance
            predictions = self.model.predict(X_scaled)
            anomaly_count = np.sum(predictions == -1)
            anomaly_percentage = (anomaly_count / len(predictions)) * 100
            
            logger.info(f"Model evaluation: {anomaly_count}/{len(predictions)} transactions flagged as anomalous ({anomaly_percentage:.1f}%)")
            
            # Save the model
            success = self.save_model()
            if success:
                logger.info("ML model training completed successfully")
            else:
                logger.error("Failed to save trained model")
            
            return success
            
        except ImportError:
            logger.error("scikit-learn not available. Using rule-based detection only.")
            return False
        except Exception as e:
            logger.error(f"Error training ML model: {e}")
            return False
    
    def predict(self, transaction):
        """Predict anomaly score for a transaction with logging
        
        Returns:
            float: Normalized risk score between 0-1 where:
                   0.0-0.3 = Low risk (normal transaction)
                   0.3-0.6 = Medium risk (slightly suspicious)
                   0.6-1.0 = High risk (anomalous, triggers OTP)
        """
        if self.model is None:
            logger.warning("ML model not available, using fallback score")
            log_system_event(
                "ML model not available for prediction",
                "fraud_ml_model",
                "WARNING",
                {"transaction_id": transaction.id}
            )
            return 0.5  # Neutral score
        
        try:
            logger.info(f"Making enhanced ML prediction for transaction {transaction.id}")
            start_time = time.time()
            
            features = self.prepare_features(transaction)
            
            # Get enhanced location features for logging
            from apps.risk.engine import RiskEngine
            risk_engine = RiskEngine()
            location_features = risk_engine.calculate_enhanced_location_features(transaction)
            
            # Scale features using the same scaler from training
            if self.scaler is not None:
                features_scaled = self.scaler.transform(features)
            else:
                # Fallback scaling
                from sklearn.preprocessing import StandardScaler
                scaler = StandardScaler()
                features_scaled = scaler.fit_transform(features)
            
            # Get anomaly score (negative values indicate anomalies)
            score = self.model.decision_function(features_scaled)[0]
            
            # Convert to 0-1 scale where 1 is most anomalous
            # Isolation Forest scores typically range from -0.5 to +0.5
            # Negative scores = anomalies, Positive scores = normal
            normalized_score = 1 - (score + 0.5)  # Convert to 0-1 scale
            normalized_score = max(0, min(1, normalized_score))  # Clamp to [0,1]
            
            processing_time = time.time() - start_time
            
            logger.info(f"Enhanced ML prediction: Raw score={score:.4f}, Normalized score={normalized_score:.4f}")
            logger.info(f"Location analysis - Distance from home: {location_features['distance_from_home']:.2f}km, "
                       f"Distance from last known: {location_features['distance_from_last_known']:.2f}km, "
                       f"Effective distance: {location_features['effective_distance']:.2f}km")
            
            # Enhanced prediction logging with detailed location intelligence
            log_prediction(
                model_name="Enhanced Fraud Detection with Effective Distance",
                input_data={
                    "transaction_id": transaction.id,
                    "amount": transaction.amount,
                    "type": transaction.transaction_type,
                    "distance_from_home": location_features['distance_from_home'],
                    "distance_from_last_known": location_features['distance_from_last_known'],
                    "effective_distance": location_features['effective_distance'],
                    "location_intelligence": f"Closest to {'HOME' if location_features['distance_from_home'] <= location_features['distance_from_last_known'] else 'LAST_KNOWN'}"
                },
                prediction=normalized_score,
                confidence=normalized_score,
                processing_time=processing_time
            )
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"Error making ML prediction for transaction {transaction.id}: {e}")
            log_system_event(
                "Error making ML prediction",
                "fraud_ml_model",
                "ERROR",
                {"transaction_id": transaction.id, "error": str(e)}
            )
            return 0.5  # Neutral score
    
    def update_client_statistics(self):
        """Update client avg_amount and std_amount based on transaction history with logging"""
        logger.info("Starting client statistics update...")
        
        updated_count = 0
        for client in ClientProfile.objects.all():
            try:
                transactions = Transaction.objects.filter(client=client)
                
                if transactions.exists():
                    stats = transactions.aggregate(
                        avg_amount=Avg('amount'),
                        std_amount=StdDev('amount')
                    )
                    
                    old_avg = client.avg_amount
                    old_std = client.std_amount
                    
                    client.avg_amount = stats['avg_amount'] or 0
                    client.std_amount = stats['std_amount'] or 0
                    client.save()
                    
                    updated_count += 1
                    logger.info(f"Updated statistics for client {client.full_name}: avg={client.avg_amount:.2f}, std={client.std_amount:.2f}")
                else:
                    logger.info(f"No transactions found for client {client.full_name}")
                    
            except Exception as e:
                logger.error(f"Error updating statistics for client {client.full_name}: {e}")
        
        logger.info(f"Client statistics update completed: {updated_count} clients updated")
    
    def get_model_info(self):
        """Get information about the current model"""
        info = {
            'model_loaded': self.model is not None,
            'model_path': self.model_path,
            'model_exists': os.path.exists(self.model_path) if self.model_path else False,
            'scaler_available': self.scaler is not None
        }
        
        if self.model is not None:
            info.update({
                'model_type': type(self.model).__name__,
                'n_estimators': getattr(self.model, 'n_estimators', 'N/A'),
                'contamination': getattr(self.model, 'contamination', 'N/A')
            })
        
        return info
