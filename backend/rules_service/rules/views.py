from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
import requests

class CheckTransaction(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        transaction = request.data
        rules_triggered = []
        
        # Check amount threshold
        if transaction['amount'] > 10000:
            rules_triggered.append('large_amount')
            
        # Check for rapid succession
        recent_transactions = self._get_recent_transactions(
            transaction['user_id'], 
            minutes=5
        )
        if len(recent_transactions) > 3:
            rules_triggered.append('rapid_succession')
            
        # Get AI service fraud score
        ai_score = self._get_ai_score(transaction)
        
        result = {
            'is_fraudulent': len(rules_triggered) > 0 or ai_score > 0.7,
            'rules_triggered': rules_triggered,
            'fraud_score': ai_score
        }
        
        if result['is_fraudulent']:
            self._send_alert(transaction, result)
            
        return Response(result)

    def _get_recent_transactions(self, user_id, minutes):
        response = requests.get(
            f'http://transaction-service:8000/api/transactions/',
            params={'user_id': user_id, 'minutes': minutes}
        )
        return response.json()

    def _get_ai_score(self, transaction):
        response = requests.post(
            'http://ai-service:8000/api/score/',
            json=transaction
        )
        return response.json()['score']

    def _send_alert(self, transaction, result):
        requests.post(
            'http://alert-service:8000/api/alerts/',
            json={
                'transaction': transaction,
                'fraud_details': result
            }
        )
