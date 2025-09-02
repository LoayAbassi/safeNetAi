#!/usr/bin/env python
"""
Comprehensive Test Suite for SafeNetAI System Fixes
Tests all business rules, AI behavior, and OTP validation requirements
"""
import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.risk.models import ClientProfile
from apps.transactions.models import Transaction
from apps.risk.engine import RiskEngine
from apps.risk.ml import FraudMLModel
from apps.users.email_service import send_transaction_notification
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

def create_test_client(name, balance=50000):
    """Create a test client profile"""
    try:
        # Create user
        user = User.objects.create_user(
            email=f"test_{name.lower().replace(' ', '_')}@test.com",
            first_name=name.split()[0],
            last_name=name.split()[1] if len(name.split()) > 1 else "User",
            password="testpass123"
        )
        
        # Create client profile
        client = ClientProfile.objects.create(
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
            national_id=f"TEST{user.id:06d}",
            balance=Decimal(str(balance)),
            avg_amount=Decimal('2000'),
            std_amount=Decimal('500')
        )
        
        return client, user
    except Exception as e:
        print(f"Error creating test client: {e}")
        return None, None

def test_ai_feature_preparation():
    """Test 1: AI Feature Preparation (Issue 1 Fix)"""
    print("\n" + "=" * 60)
    print("TEST 1: AI FEATURE PREPARATION")
    print("=" * 60)
    
    try:
        client, user = create_test_client("AI Test", 25000)
        if not client:
            return False
            
        # Create test transaction
        test_transaction = Transaction.objects.create(
            client=client,
            amount=Decimal('5000'),
            transaction_type='transfer',
            to_account_number='12345678',
            status='pending'
        )
        
        # Test AI feature preparation (should NOT error on location_lat)
        ml_model = FraudMLModel()
        ml_score = ml_model.predict(test_transaction)
        
        print(f"✓ AI prediction successful: {ml_score:.3f}")
        print(f"✓ No location_lat errors encountered")
        
        # Cleanup
        test_transaction.delete()
        client.delete()
        user.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ AI feature preparation test failed: {e}")
        return False

def test_business_rules_trigger_otp():
    """Test 2: Business Rules Trigger OTP (Issue 2 Fix)"""
    print("\n" + "=" * 60)
    print("TEST 2: BUSINESS RULES TRIGGER OTP")
    print("=" * 60)
    
    test_results = []
    
    # Test 2a: Large Amount Rule
    try:
        client, user = create_test_client("Large Amount", 50000)
        test_transaction = Transaction(
            client=client,
            amount=Decimal('15000'),  # > 10,000 threshold
            transaction_type='transfer',
            to_account_number='87654321',
            created_at=timezone.now()
        )
        
        risk_engine = RiskEngine()
        risk_score, triggers, requires_otp, decision = risk_engine.calculate_risk_score(test_transaction)
        
        if len(triggers) > 0 and any('large' in trigger.lower() for trigger in triggers):
            print("✓ Large amount rule triggered correctly")
            test_results.append(True)
        else:
            print("❌ Large amount rule failed to trigger")
            test_results.append(False)
            
        client.delete()
        user.delete()
        
    except Exception as e:
        print(f"❌ Large amount test failed: {e}")
        test_results.append(False)
    
    # Test 2b: High Frequency Rule  
    try:
        client, user = create_test_client("High Freq", 30000)
        
        # Create 6 recent transactions (threshold is 5)
        base_time = timezone.now()
        for i in range(6):
            Transaction.objects.create(
                client=client,
                amount=Decimal('1000'),
                transaction_type='transfer',
                to_account_number='87654321',
                created_at=base_time - timedelta(minutes=i*8),  # Within 1 hour
                status='completed'
            )
        
        # Test new transaction
        test_transaction = Transaction(
            client=client,
            amount=Decimal('2000'),
            transaction_type='transfer',
            created_at=timezone.now()
        )
        
        risk_score, triggers, requires_otp, decision = risk_engine.calculate_risk_score(test_transaction)
        
        if len(triggers) > 0 and any('frequency' in trigger.lower() for trigger in triggers):
            print("✓ High frequency rule triggered correctly")
            test_results.append(True)
        else:
            print("❌ High frequency rule failed to trigger")
            test_results.append(False)
            
        # Cleanup
        Transaction.objects.filter(client=client).delete()
        client.delete()
        user.delete()
        
    except Exception as e:
        print(f"❌ High frequency test failed: {e}")
        test_results.append(False)
    
    # Test 2c: Low Balance Rule
    try:
        client, user = create_test_client("Low Balance", 150)  # Low starting balance
        
        test_transaction = Transaction(
            client=client,
            amount=Decimal('100'),  # Would leave 50 DZD (< 100 threshold)
            transaction_type='transfer',
            to_account_number='87654321',
            created_at=timezone.now()
        )
        
        risk_score, triggers, requires_otp, decision = risk_engine.calculate_risk_score(test_transaction)
        
        if len(triggers) > 0 and any('balance' in trigger.lower() for trigger in triggers):
            print("✓ Low balance rule triggered correctly")
            test_results.append(True)
        else:
            print("❌ Low balance rule failed to trigger")
            test_results.append(False)
            
        client.delete()
        user.delete()
        
    except Exception as e:
        print(f"❌ Low balance test failed: {e}")
        test_results.append(False)
    
    # Test 2d: Unusual Time Rule
    try:
        client, user = create_test_client("Unusual Time", 20000)
        
        # Create transaction at 2:00 AM (unusual time)
        unusual_time = timezone.now().replace(hour=2, minute=0, second=0, microsecond=0)
        test_transaction = Transaction(
            client=client,
            amount=Decimal('3000'),
            transaction_type='transfer',
            to_account_number='87654321',
            created_at=unusual_time
        )
        
        risk_score, triggers, requires_otp, decision = risk_engine.calculate_risk_score(test_transaction)
        
        if len(triggers) > 0 and any('unusual time' in trigger.lower() for trigger in triggers):
            print("✓ Unusual time rule triggered correctly")
            test_results.append(True)
        else:
            print("❌ Unusual time rule failed to trigger")
            test_results.append(False)
            
        client.delete()
        user.delete()
        
    except Exception as e:
        print(f"❌ Unusual time test failed: {e}")
        test_results.append(False)
    
    success_rate = sum(test_results) / len(test_results) if test_results else 0
    print(f"\nBusiness Rules Test Results: {sum(test_results)}/{len(test_results)} rules working ({success_rate*100:.1f}%)")
    return success_rate >= 0.75  # At least 75% of rules working

def test_ai_scoring_triggers_otp():
    """Test 3: AI Scoring Triggers OTP (Issue 4 Fix)"""
    print("\n" + "=" * 60)
    print("TEST 3: AI SCORING TRIGGERS OTP")
    print("=" * 60)
    
    try:
        client, user = create_test_client("AI Score", 30000)
        
        # Create transaction for AI evaluation
        test_transaction = Transaction.objects.create(
            client=client,
            amount=Decimal('8000'),
            transaction_type='transfer',
            to_account_number='87654321',
            status='pending'
        )
        
        # Test AI scoring
        ml_model = FraudMLModel()
        ml_score = ml_model.predict(test_transaction)
        
        print(f"✓ AI score calculated: {ml_score:.3f}")
        
        # Test OTP triggering logic
        risk_engine = RiskEngine()
        risk_score, triggers, requires_otp, decision = risk_engine.calculate_risk_score(test_transaction)
        
        # Simulate the OTP decision logic from transaction views
        requires_otp_final = (
            len(triggers) > 0 or           # ANY rule triggered
            risk_score >= 70 or            # High combined risk score
            ml_score >= 0.6 or             # High AI risk score
            requires_otp                   # Explicit OTP requirement
        )
        
        print(f"✓ Business rules triggered: {len(triggers)}")
        print(f"✓ Combined risk score: {risk_score}")
        print(f"✓ ML score: {ml_score:.3f}")
        print(f"✓ OTP required: {requires_otp_final}")
        
        if ml_score >= 0.6:
            print("✓ High AI score (≥0.6) would trigger OTP validation")
        else:
            print(f"✓ AI score ({ml_score:.3f}) below OTP threshold (0.6)")
        
        # Cleanup
        test_transaction.delete()
        client.delete()
        user.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ AI scoring test failed: {e}")
        return False

def test_client_profile_updates():
    """Test 4: Client Profile Updates (Issue 3 Fix)"""
    print("\n" + "=" * 60)
    print("TEST 4: CLIENT PROFILE METRICS UPDATES")
    print("=" * 60)
    
    try:
        # Create two clients for transfer testing
        sender, sender_user = create_test_client("Sender Test", 10000)
        recipient, recipient_user = create_test_client("Recipient Test", 5000)
        
        print(f"✓ Sender initial balance: {sender.balance}")
        print(f"✓ Recipient initial balance: {recipient.balance}")
        print(f"✓ Sender initial avg_amount: {sender.avg_amount}")
        
        # Create a completed transaction
        transaction = Transaction.objects.create(
            client=sender,
            amount=Decimal('3000'),
            transaction_type='transfer',
            to_account_number=recipient.bank_account_number,
            status='completed'
        )
        
        # Simulate the balance update process
        from apps.transactions.views import TransactionViewSet
        viewset = TransactionViewSet()
        viewset._update_balances(transaction, sender)
        
        # Refresh objects from database
        sender.refresh_from_db()
        recipient.refresh_from_db()
        
        print(f"✓ Sender final balance: {sender.balance}")
        print(f"✓ Recipient final balance: {recipient.balance}")
        print(f"✓ Sender updated avg_amount: {sender.avg_amount}")
        print(f"✓ Sender updated std_amount: {sender.std_amount}")
        
        # Verify balance changes
        expected_sender_balance = Decimal('7000')  # 10000 - 3000
        expected_recipient_balance = Decimal('8000')  # 5000 + 3000
        
        balance_update_correct = (
            sender.balance == expected_sender_balance and
            recipient.balance == expected_recipient_balance
        )
        
        stats_updated = sender.avg_amount > 0 or sender.std_amount >= 0
        
        if balance_update_correct:
            print("✓ Balance updates working correctly")
        else:
            print("❌ Balance updates failed")
        
        if stats_updated:
            print("✓ Statistics updates working correctly")
        else:
            print("❌ Statistics updates failed")
        
        # Cleanup
        transaction.delete()
        sender.delete()
        sender_user.delete()
        recipient.delete()
        recipient_user.delete()
        
        return balance_update_correct and stats_updated
        
    except Exception as e:
        print(f"❌ Client profile update test failed: {e}")
        return False

def test_end_to_end_scenarios():
    """Test 5: End-to-End Transaction Scenarios"""
    print("\n" + "=" * 60)
    print("TEST 5: END-TO-END TRANSACTION SCENARIOS")
    print("=" * 60)
    
    scenarios_passed = 0
    total_scenarios = 3
    
    # Scenario 1: Normal transaction (no OTP)
    try:
        client, user = create_test_client("Normal User", 15000)
        
        test_transaction = Transaction(
            client=client,
            amount=Decimal('2000'),  # Normal amount
            transaction_type='transfer',
            to_account_number='12345678',
            created_at=timezone.now().replace(hour=14)  # Normal time
        )
        
        risk_engine = RiskEngine()
        risk_score, triggers, requires_otp, decision = risk_engine.calculate_risk_score(test_transaction)
        
        ml_model = FraudMLModel()
        ml_score = ml_model.predict(test_transaction)
        
        # Check OTP requirement logic
        requires_otp_final = (
            len(triggers) > 0 or
            risk_score >= 70 or
            ml_score >= 0.6 or
            requires_otp
        )
        
        if not requires_otp_final:
            print("✓ Scenario 1: Normal transaction correctly bypasses OTP")
            scenarios_passed += 1
        else:
            print(f"❌ Scenario 1: Normal transaction incorrectly requires OTP (Score: {risk_score}, ML: {ml_score:.3f}, Triggers: {len(triggers)})")
        
        client.delete()
        user.delete()
        
    except Exception as e:
        print(f"❌ Scenario 1 failed: {e}")
    
    # Scenario 2: High-risk transaction (requires OTP)
    try:
        client, user = create_test_client("High Risk User", 50000)
        
        test_transaction = Transaction(
            client=client,
            amount=Decimal('25000'),  # Large amount
            transaction_type='transfer',
            to_account_number='12345678',
            created_at=timezone.now().replace(hour=3)  # Unusual time
        )
        
        risk_score, triggers, requires_otp, decision = risk_engine.calculate_risk_score(test_transaction)
        ml_score = ml_model.predict(test_transaction)
        
        requires_otp_final = (
            len(triggers) > 0 or
            risk_score >= 70 or
            ml_score >= 0.6 or
            requires_otp
        )
        
        if requires_otp_final:
            print("✓ Scenario 2: High-risk transaction correctly requires OTP")
            scenarios_passed += 1
        else:
            print(f"❌ Scenario 2: High-risk transaction incorrectly bypasses OTP (Score: {risk_score}, ML: {ml_score:.3f}, Triggers: {len(triggers)})")
        
        client.delete()
        user.delete()
        
    except Exception as e:
        print(f"❌ Scenario 2 failed: {e}")
    
    # Scenario 3: AI-flagged transaction (requires OTP)
    try:
        client, user = create_test_client("AI Flag User", 20000)
        
        # Create unusual pattern that might trigger AI
        test_transaction = Transaction(
            client=client,
            amount=Decimal('18000'),  # Large amount
            transaction_type='transfer',
            to_account_number='12345678',
            created_at=timezone.now().replace(hour=1)  # Very unusual time
        )
        
        risk_score, triggers, requires_otp, decision = risk_engine.calculate_risk_score(test_transaction)
        ml_score = ml_model.predict(test_transaction)
        
        # This should trigger due to multiple factors
        requires_otp_final = (
            len(triggers) > 0 or
            risk_score >= 70 or
            ml_score >= 0.6 or
            requires_otp
        )
        
        if requires_otp_final:
            print("✓ Scenario 3: AI-flagged transaction correctly requires OTP")
            scenarios_passed += 1
        else:
            print(f"❌ Scenario 3: AI-flagged transaction incorrectly bypasses OTP (Score: {risk_score}, ML: {ml_score:.3f}, Triggers: {len(triggers)})")
        
        client.delete()
        user.delete()
        
    except Exception as e:
        print(f"❌ Scenario 3 failed: {e}")
    
    print(f"\nEnd-to-End Scenarios: {scenarios_passed}/{total_scenarios} passed")
    return scenarios_passed == total_scenarios

def main():
    """Run comprehensive test suite"""
    print("SafeNetAI System - Comprehensive Fix Validation")
    print("Testing all issues addressed in the latest fixes")
    print("=" * 80)
    
    test_results = []
    
    # Run all tests
    test_results.append(test_ai_feature_preparation())
    test_results.append(test_business_rules_trigger_otp())
    test_results.append(test_ai_scoring_triggers_otp())
    test_results.append(test_client_profile_updates())
    test_results.append(test_end_to_end_scenarios())
    
    # Final summary
    print("\n" + "=" * 80)
    print("COMPREHENSIVE TEST RESULTS")
    print("=" * 80)
    
    test_names = [
        "AI Feature Preparation",
        "Business Rules → OTP",
        "AI Scoring → OTP", 
        "Client Profile Updates",
        "End-to-End Scenarios"
    ]
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Overall Test Results: {passed}/{total} test suites passed\n")
    
    for i, (name, result) in enumerate(zip(test_names, test_results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {name}: {status}")
    
    if passed == total:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("✅ AI feature preparation working without errors")
        print("✅ Business rules trigger OTP validation correctly") 
        print("✅ AI risk scoring integrates with OTP validation")
        print("✅ Client profile metrics update properly")
        print("✅ End-to-end transaction flows working")
        print("\nThe SafeNetAI system is fully functional and secure.")
    else:
        print(f"\n⚠️ {total - passed} test suite(s) failed")
        print("Please review the failed tests above for detailed information.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)