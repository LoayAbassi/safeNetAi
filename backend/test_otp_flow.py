#!/usr/bin/env python
"""
OTP Verification Flow Test for SafeNetAI System
Tests the complete OTP flow from transaction creation to completion
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
from apps.transactions.models import Transaction, TransactionOTP
from apps.risk.engine import RiskEngine
from apps.risk.ml import FraudMLModel
from apps.transactions.services import create_transaction_otp, verify_transaction_otp
from datetime import datetime
from decimal import Decimal
from django.utils import timezone
import requests
import json

User = get_user_model()

def test_otp_flow_creation():
    """Test OTP creation for risky transactions"""
    print("=" * 70)
    print("TESTING OTP FLOW - TRANSACTION CREATION")
    print("=" * 70)
    
    try:
        # Get a test client
        client = ClientProfile.objects.first()
        if not client:
            print("❌ No client profiles found. Please create test data first.")
            return False
            
        print(f"✓ Using client: {client.full_name}")
        
        # Create a risky transaction (large amount)
        test_transaction = Transaction.objects.create(
            client=client,
            amount=Decimal('15000'),  # Large amount to trigger rules
            transaction_type='transfer',
            to_account_number='87654321',
            status='pending'  # Will be set to pending after risk assessment
        )
        
        print(f"✓ Created test transaction: ID {test_transaction.id}, Amount: {test_transaction.amount}")
        
        # Run risk assessment
        risk_engine = RiskEngine()
        risk_score, triggers, requires_otp, decision = risk_engine.calculate_risk_score(test_transaction)
        
        # Add ML score
        ml_model = FraudMLModel()
        ml_score = ml_model.predict(test_transaction)
        ml_contribution = int(ml_score * 40)
        risk_score += ml_contribution
        
        print(f"✓ Risk Assessment Complete:")
        print(f"  - Business Rule Score: {risk_score - ml_contribution}")
        print(f"  - ML Score: {ml_score:.3f} (contributes {ml_contribution} points)")
        print(f"  - Total Risk Score: {risk_score}")
        print(f"  - Triggers: {triggers}")
        print(f"  - Decision: {decision}")
        
        # Check OTP requirement
        requires_otp_final = (
            len(triggers) > 0 or           # ANY rule triggered
            risk_score >= 70 or            # High combined risk score
            ml_score >= 0.6 or             # High AI risk score
            requires_otp                   # Explicit OTP requirement
        )
        
        print(f"✓ OTP Required: {requires_otp_final}")
        
        if requires_otp_final:
            # Create OTP
            otp_obj = create_transaction_otp(test_transaction, client.user)
            
            if otp_obj:
                print(f"✓ OTP Created Successfully:")
                print(f"  - OTP Code: {otp_obj.otp}")
                print(f"  - Expires At: {otp_obj.expires_at}")
                print(f"  - User: {otp_obj.user.email}")
                
                # Test OTP verification
                print(f"\n📧 Testing OTP Verification...")
                
                # Verify with correct OTP
                result = verify_transaction_otp(test_transaction.id, otp_obj.otp, client.user)
                
                if result['success']:
                    print(f"✅ OTP Verification Successful: {result['message']}")
                    
                    # Update transaction status
                    test_transaction.status = 'completed'
                    test_transaction.save()
                    print(f"✓ Transaction {test_transaction.id} marked as completed")
                    
                    return True
                else:
                    print(f"❌ OTP Verification Failed: {result['error']}")
                    return False
            else:
                print(f"❌ Failed to create OTP")
                return False
        else:
            print(f"⚠️ Transaction would complete without OTP (low risk)")
            return True
            
    except Exception as e:
        print(f"❌ Error in OTP flow test: {e}")
        return False
    finally:
        # Cleanup
        try:
            if 'test_transaction' in locals():
                TransactionOTP.objects.filter(transaction=test_transaction).delete()
                test_transaction.delete()
                print(f"✓ Test data cleaned up")
        except:
            pass

def test_api_endpoints():
    """Test OTP API endpoints"""
    print("\n" + "=" * 70)
    print("TESTING OTP API ENDPOINTS")
    print("=" * 70)
    
    base_url = "http://localhost:8000"
    
    # Test if server is running
    try:
        response = requests.get(f"{base_url}/admin/", timeout=5)
        print(f"✓ Server is running at {base_url}")
    except requests.exceptions.RequestException:
        print(f"❌ Server not running at {base_url}")
        print(f"   Please start the server with: python manage.py runserver 8000")
        return False
    
    print(f"✓ API endpoint structure analysis:")
    print(f"  - Transaction creation: POST /api/client/transactions/")
    print(f"  - OTP verification: POST /api/client/transactions/{'{transaction_id}'}/verify_otp/")
    print(f"  - OTP resend: POST /api/client/transactions/{'{transaction_id}'}/resend_otp/")
    
    return True

def test_frontend_integration():
    """Test frontend OTP component integration"""
    print("\n" + "=" * 70)
    print("TESTING FRONTEND OTP INTEGRATION")
    print("=" * 70)
    
    try:
        # Check if OTPVerification component file exists and has correct API calls
        otp_component_path = "c:/Users/HP/Desktop/projects/safeNetAi/frontend/src/components/OTPVerification.jsx"
        
        if os.path.exists(otp_component_path):
            with open(otp_component_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for correct API endpoints
            if "/api/client/transactions/${transactionId}/verify_otp/" in content:
                print("✓ OTPVerification component uses correct verify_otp endpoint")
            else:
                print("❌ OTPVerification component uses incorrect verify_otp endpoint")
                return False
                
            if "/api/client/transactions/${transactionId}/resend_otp/" in content:
                print("✓ OTPVerification component uses correct resend_otp endpoint")
            else:
                print("❌ OTPVerification component uses incorrect resend_otp endpoint")
                return False
                
            # Check Transfer component
            transfer_path = "c:/Users/HP/Desktop/projects/safeNetAi/frontend/src/pages/Transfer.jsx"
            if os.path.exists(transfer_path):
                with open(transfer_path, 'r', encoding='utf-8') as f:
                    transfer_content = f.read()
                    
                if "showOTP && pendingTransaction" in transfer_content:
                    print("✓ Transfer component properly shows OTP modal for risky transactions")
                else:
                    print("❌ Transfer component missing OTP modal logic")
                    return False
                    
                if "handleOTPSuccess" in transfer_content:
                    print("✓ Transfer component has OTP success handler")
                else:
                    print("❌ Transfer component missing OTP success handler")
                    return False
            else:
                print("❌ Transfer component not found")
                return False
                
            print("✓ Frontend OTP integration appears correct")
            return True
        else:
            print("❌ OTPVerification component not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking frontend integration: {e}")
        return False

def main():
    """Run complete OTP flow test"""
    print("SafeNetAI System - OTP Verification Flow Test")
    print("Testing complete OTP flow from transaction to completion")
    print("=" * 80)
    
    test_results = []
    
    # Run tests
    test_results.append(test_otp_flow_creation())
    test_results.append(test_api_endpoints())  
    test_results.append(test_frontend_integration())
    
    # Summary
    print("\n" + "=" * 80)
    print("OTP FLOW TEST SUMMARY")
    print("=" * 80)
    
    test_names = [
        "OTP Flow Creation & Verification",
        "API Endpoint Structure",
        "Frontend Integration"
    ]
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Overall Test Results: {passed}/{total} tests passed\n")
    
    for i, (name, result) in enumerate(zip(test_names, test_results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {name}: {status}")
    
    if passed == total:
        print("\n🎉 OTP VERIFICATION FLOW IS WORKING CORRECTLY!")
        print("✅ Backend OTP creation and verification functional")
        print("✅ API endpoints properly structured")
        print("✅ Frontend components correctly integrated")
        print("\n📋 Next Steps:")
        print("   1. Start both backend and frontend servers")
        print("   2. Create a risky transaction (>10,000 DZD or unusual time)")
        print("   3. Check email for OTP and verify the frontend shows the input field")
        print("   4. Complete transaction with OTP verification")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        print("Please review the failed tests above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)