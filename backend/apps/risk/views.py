from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .ml import FraudMLModel

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_fraud(request):
    """AI endpoint for fraud prediction"""
    try:
        # Get transaction data from request
        transaction_data = request.data
        
        # Create a mock transaction object for prediction
        # In a real implementation, you'd get the actual transaction
        from apps.transactions.models import Transaction
        from apps.risk.models import ClientProfile
        
        # This is a simplified version - in practice you'd validate the data
        # and create a proper transaction object
        client_profile = ClientProfile.objects.get(user=request.user)
        
        # Create a temporary transaction for prediction
        transaction = Transaction(
            client=client_profile,
            amount=transaction_data.get('amount', 0),
            transaction_type=transaction_data.get('transaction_type', 'transfer'),
            location_lat=transaction_data.get('location_lat'),
            location_lng=transaction_data.get('location_lng'),
        )
        
        # Get ML prediction
        ml_model = FraudMLModel()
        anomaly_score = ml_model.predict(transaction)
        
        return Response({
            'anomaly_score': anomaly_score,
            'is_anomalous': anomaly_score > 0.7,  # Threshold for anomaly
            'confidence': 1 - anomaly_score
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
