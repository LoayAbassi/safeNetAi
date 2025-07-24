import random
import time
import uuid
import requests
from datetime import datetime

class TransactionSimulator:
    def __init__(self):
        self.transaction_types = ['transfer', 'deposit', 'withdrawal']
        self.users = range(1, 100)  # Simulate 100 users
        self.base_url = 'http://transaction-service:8000/api/transactions/'

    def generate_transaction(self):
        return {
            'transaction_id': str(uuid.uuid4()),
            'user_id': random.choice(self.users),
            'amount': round(random.uniform(10, 15000), 2),
            'transaction_type': random.choice(self.transaction_types),
            'source_account': f'ACC{random.randint(1000, 9999)}',
            'destination_account': f'ACC{random.randint(1000, 9999)}',
            'timestamp': datetime.now().isoformat()
        }

    def run(self, interval=5):
        while True:
            transaction = self.generate_transaction()
            try:
                response = requests.post(self.base_url, json=transaction)
                print(f"Sent transaction: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Error sending transaction: {e}")
            time.sleep(interval)

if __name__ == '__main__':
    simulator = TransactionSimulator()
    simulator.run()
