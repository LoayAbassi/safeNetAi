from django.core.management.base import BaseCommand
from apps.risk.ml import FraudMLModel

class Command(BaseCommand):
    help = 'Train the fraud detection model using historical transaction data'

    def handle(self, *args, **options):
        self.stdout.write('Starting fraud model training...')
        
        # Update client statistics first
        ml_model = FraudMLModel()
        ml_model.update_client_statistics()
        self.stdout.write('Updated client statistics.')
        
        # Train the model
        success = ml_model.train()
        
        if success:
            self.stdout.write(
                self.style.SUCCESS('Successfully trained and saved fraud detection model.')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Model training failed or insufficient data. Using rule-based detection only.')
            )
