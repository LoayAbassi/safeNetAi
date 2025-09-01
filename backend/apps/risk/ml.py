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
                self.model = joblib.load(self.model_path)
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
        """Prepare features for a single transaction with logging"""
        try:
            client = transaction.client
            
            logger.info(f"Preparing features for transaction {transaction.id}")
            
            # Basic transaction features
            features = [
                float(transaction.amount),
                float(client.balance),
                float(client.avg_amount) if client.avg_amount > 0 else 0,
                float(client.std_amount) if client.std_amount > 0 else 0,
            ]
            
            # Transaction type encoding
            type_encoding = {'deposit': 0, 'withdraw': 1, 'transfer': 2}
            features.append(type_encoding.get(transaction.transaction_type, 0))
            
            # Time-based features
            hour = transaction.created_at.hour
            day_of_week = transaction.created_at.weekday()
            features.extend([hour, day_of_week])
            
            # Location features (if available)
            if transaction.location_lat and transaction.location_lng:
                features.extend([float(transaction.location_lat), float(transaction.location_lng)])
            else:
                features.extend([0, 0])
            
            # Recent transaction count
            recent_count = Transaction.objects.filter(
                client=client,
                created_at__gte=transaction.created_at - pd.Timedelta(hours=1)
            ).count()
            features.append(recent_count)
            
            # Additional features for better detection
            # Time since last transaction
            last_transaction = Transaction.objects.filter(
                client=client
            ).exclude(id=transaction.id).order_by('-created_at').first()
            
            if last_transaction:
                time_diff = (transaction.created_at - last_transaction.created_at).total_seconds() / 3600  # hours
                features.append(time_diff)
            else:
                features.append(24)  # Default to 24 hours if no previous transaction
            
            # Account age (days since creation)
            account_age = (transaction.created_at - client.created_at).days
            features.append(account_age)
            
            # Balance ratio (current balance / average transaction amount)
            if client.avg_amount > 0:
                balance_ratio = float(client.balance) / float(client.avg_amount)
            else:
                balance_ratio = 1.0
            features.append(balance_ratio)
            
            feature_array = np.array(features).reshape(1, -1)
            logger.info(f"Features prepared: {len(features)} features, shape: {feature_array.shape}")
            
            return feature_array
            
        except Exception as e:
            logger.error(f"Error preparing features for transaction {transaction.id}: {e}")
            # Return default features
            return np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
    
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
        """Predict anomaly score for a transaction with logging"""
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
            logger.info(f"Making ML prediction for transaction {transaction.id}")
            start_time = time.time()
            
            features = self.prepare_features(transaction)
            
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
            normalized_score = 1 - (score + 0.5)  # Assuming scores are roughly in [-0.5, 0.5]
            normalized_score = max(0, min(1, normalized_score))
            
            processing_time = time.time() - start_time
            
            logger.info(f"ML prediction: Raw score={score:.4f}, Normalized score={normalized_score:.4f}")
            
            # Log prediction using structured logging
            log_prediction(
                model_name="Fraud Detection Isolation Forest",
                input_data={"transaction_id": transaction.id, "amount": transaction.amount, "type": transaction.transaction_type},
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
