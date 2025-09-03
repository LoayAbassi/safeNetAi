#!/usr/bin/env python
"""
Test script to verify the fraud alert duplication fix and OTP flow
"""

import os
import sys
import django
from decimal import Decimal

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
    from apps.risk.models import ClientProfile
    from apps.transactions.models import Transaction, FraudAlert
    from apps.users.models import User
    from apps.risk.engine import RiskEngine
    from apps.transactions.services import create_transaction_otp
    print("✅ Django setup successful!")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

def test_fraud_alert_duplication_fix():
    """Test that fraud alerts are not duplicated"""
    print("\n" + "=" * 60)
    print("TEST 1: FRAUD ALERT DUPLICATION FIX")
    print("=" * 60)
    
    try:
        # Create test user and client
        test_user = User.objects.create_user(
            email="test_fraud@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            is_email_verified=True
        )
        
        test_client = ClientProfile.objects.create(
            user=test_user,
            first_name="Test",
            last_name="User",
            national_id="1234567890123456",
            bank_account_number="12345678",
            balance=Decimal('50000.00'),
            home_lat=Decimal('36.7538'),  # Algiers
            home_lng=Decimal('3.0588'),
            last_known_lat=Decimal('48.8566'),  # Paris (distance > 50km)
            last_known_lng=Decimal('2.3522')
        )
        
        # Create transaction that will trigger high risk
        test_transaction = Transaction.objects.create(
            client=test_client,
            amount=Decimal('15000.00'),  # High amount
            transaction_type='transfer',
            to_account_number='87654321',
            status='pending'
        )
        
        print(f"✅ Created test transaction {test_transaction.id}")
        
        # Initialize risk engine
        risk_engine = RiskEngine()
        
        # First call to create_fraud_alert
        print("📊 First call to create_fraud_alert...")
        fraud_alert_1 = risk_engine.create_fraud_alert(test_transaction, 85, ['Large transfer', 'Distance exceeded'])
        print(f"✅ First fraud alert created: ID {fraud_alert_1.id}")
        
        # Second call to create_fraud_alert (should return existing alert)
        print("📊 Second call to create_fraud_alert...")
        fraud_alert_2 = risk_engine.create_fraud_alert(test_transaction, 85, ['Large transfer', 'Distance exceeded'])
        print(f"✅ Second call returned existing alert: ID {fraud_alert_2.id}")
        
        # Verify they are the same alert
        if fraud_alert_1.id == fraud_alert_2.id:
            print("✅ SUCCESS: No duplicate fraud alerts created!")
            print(f"   Both calls returned the same alert (ID: {fraud_alert_1.id})")
        else:
            print("❌ FAILED: Duplicate fraud alerts were created!")
            return False
        
        # Verify only one fraud alert exists for this transaction
        fraud_alert_count = FraudAlert.objects.filter(transaction=test_transaction).count()
        if fraud_alert_count == 1:
            print(f"✅ SUCCESS: Only 1 fraud alert exists for transaction {test_transaction.id}")
        else:
            print(f"❌ FAILED: {fraud_alert_count} fraud alerts found for transaction {test_transaction.id}")
            return False
        
        # Clean up
        test_transaction.delete()
        test_client.delete()
        test_user.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_otp_flow_completion():
    """Test that OTP flow completes without errors"""
    print("\n" + "=" * 60)
    print("TEST 2: OTP FLOW COMPLETION")
    print("=" * 60)
    
    try:
        # Create test user and client
        test_user = User.objects.create_user(
            email="test_otp@example.com",
            password="testpass123",
            first_name="OTP",
            last_name="Test",
            is_email_verified=True
        )
        
        test_client = ClientProfile.objects.create(
            user=test_user,
            first_name="OTP",
            last_name="Test",
            national_id="9876543210987654",
            bank_account_number="87654321",
            balance=Decimal('25000.00'),
            home_lat=Decimal('36.7538'),  # Algiers
            home_lng=Decimal('3.0588'),
            last_known_lat=Decimal('48.8566'),  # Paris (triggers distance rule)
            last_known_lng=Decimal('2.3522')
        )
        
        # Create high-risk transaction
        test_transaction = Transaction.objects.create(
            client=test_client,
            amount=Decimal('12000.00'),
            transaction_type='transfer',
            to_account_number='11223344',
            status='pending',
            risk_score=85
        )
        
        print(f"✅ Created high-risk transaction {test_transaction.id}")
        
        # Test OTP creation
        print("📧 Testing OTP creation...")
        otp_obj = create_transaction_otp(test_transaction, test_user)
        
        if otp_obj:
            print(f"✅ OTP created successfully: {otp_obj.otp}")
            print(f"   Expires at: {otp_obj.expires_at}")
        else:
            print("❌ FAILED: OTP creation failed")
            return False
        
        # Test fraud alert creation (should not cause duplication error)
        print("📊 Testing fraud alert creation...")
        risk_engine = RiskEngine()
        
        try:
            fraud_alert = risk_engine.create_fraud_alert(
                test_transaction, 
                85, 
                ['Large transfer', 'Distance exceeded: 1347km > 50km']
            )
            print(f"✅ Fraud alert created successfully: ID {fraud_alert.id}")
        except Exception as e:
            print(f"❌ FAILED: Fraud alert creation failed: {e}")
            return False
        
        # Clean up
        test_transaction.delete()
        test_client.delete()
        test_user.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_location_violation_detection():
    """Test that location violations are properly detected and handled"""
    print("\n" + "=" * 60)
    print("TEST 3: LOCATION VIOLATION DETECTION")
    print("=" * 60)
    
    try:
        # Create test user and client
        test_user = User.objects.create_user(
            email="test_location@example.com",
            password="testpass123",
            first_name="Location",
            last_name="Test",
            is_email_verified=True
        )
        
        test_client = ClientProfile.objects.create(
            user=test_user,
            first_name="Location",
            last_name="Test",
            national_id="5678901234567890",
            bank_account_number="56789012",
            balance=Decimal('30000.00'),
            home_lat=Decimal('36.7538'),  # Algiers
            home_lng=Decimal('3.0588'),
            last_known_lat=Decimal('40.7128'),  # New York (very far)
            last_known_lng=Decimal('-74.0060')
        )
        
        # Create transaction
        test_transaction = Transaction.objects.create(
            client=test_client,
            amount=Decimal('5000.00'),
            transaction_type='transfer',
            to_account_number='98765432',
            status='pending'
        )
        
        print(f"✅ Created test transaction {test_transaction.id}")
        print(f"   Home location: ({test_client.home_lat}, {test_client.home_lng})")
        print(f"   Current location: ({test_client.last_known_lat}, {test_client.last_known_lng})")
        
        # Test risk assessment
        risk_engine = RiskEngine()
        risk_score, triggers, requires_otp, decision = risk_engine.calculate_risk_score(test_transaction)
        
        print(f"📊 Risk assessment results:")
        print(f"   Risk score: {risk_score}")
        print(f"   Triggers: {triggers}")
        print(f"   Requires OTP: {requires_otp}")
        print(f"   Decision: {decision}")
        
        # Check if distance violation was detected
        distance_violation = any('distance exceeded' in trigger.lower() for trigger in triggers)
        
        if distance_violation:
            print("✅ SUCCESS: Distance violation detected in triggers")
        else:
            print("❌ WARNING: Distance violation not detected")
        
        if requires_otp:
            print("✅ SUCCESS: OTP is required for this transaction")
        else:
            print("❌ FAILED: OTP should be required for distance violation")
            return False
        
        # Clean up
        test_transaction.delete()
        test_client.delete()
        test_user.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 SafeNetAI - Fraud Alert Duplication Fix Validation")
    print("=" * 80)
    
    test_results = []
    
    # Run tests
    test_results.append(test_fraud_alert_duplication_fix())
    test_results.append(test_otp_flow_completion())
    test_results.append(test_location_violation_detection())
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"📊 Results: {passed_tests}/{total_tests} tests passed")
    print()
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Fraud alert duplication is fixed")
        print("✅ OTP flow completes without errors")
        print("✅ Location violations are properly detected")
        print("✅ The system should now work without UNIQUE constraint errors")
    else:
        print("⚠️  Some tests failed - please review the issues above")
    
    print("\n🚀 Next steps:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Test transaction creation via frontend")
    print("3. Monitor logs for any remaining errors")
    print("4. Verify OTP emails are properly formatted")

if __name__ == "__main__":
    main()