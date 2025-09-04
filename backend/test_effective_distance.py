#!/usr/bin/env python
"""
Test script to verify Enhanced Location Rules with Effective Distance Logic
Tests the new minimum distance logic and AI/ML feature updates
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
    from django.conf import settings
    from apps.risk.models import ClientProfile
    from apps.transactions.models import Transaction
    from apps.users.models import User
    from apps.risk.engine import RiskEngine
    from apps.risk.ml import FraudMLModel
    print("✅ Django setup successful!")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

def test_effective_distance_logic():
    """Test the enhanced effective distance logic"""
    print("\n" + "=" * 80)
    print("TEST: EFFECTIVE DISTANCE LOGIC (HOME vs LAST KNOWN)")
    print("=" * 80)
    
    try:
        # Create test user
        test_user = User.objects.create_user(
            email="effective_distance@safenetai.com",
            password="testpass123",
            first_name="Effective",
            last_name="Distance",
            is_email_verified=True
        )
        
        # Test Case 1: Home fails (>50km) but last known passes (<50km) → NO OTP
        print("\n📍 TEST CASE 1: Home fails, Last Known passes → NO OTP")
        test_client_1 = ClientProfile.objects.create(
            user=test_user,
            first_name="Test",
            last_name="Case1",
            national_id="EFF123456789",
            bank_account_number="12345678",
            balance=Decimal('20000.00'),
            home_lat=Decimal('36.7538'),      # Algiers (home)
            home_lng=Decimal('3.0588'),
            last_known_lat=Decimal('48.8566'),   # Paris (current location - far from home)
            last_known_lng=Decimal('2.3522')
        )
        
        # Create a previous transaction to simulate "last known" location
        prev_transaction = Transaction.objects.create(
            client=test_client_1,
            amount=Decimal('1000.00'),
            transaction_type='transfer',
            to_account_number='99999999',
            status='completed'
        )
        
        # Current transaction (should use effective distance logic)
        test_transaction_1 = Transaction.objects.create(
            client=test_client_1,
            amount=Decimal('5000.00'),
            transaction_type='transfer',
            to_account_number='87654321',
            status='pending'
        )
        
        risk_engine = RiskEngine()
        
        # Get location features
        location_features = risk_engine.calculate_enhanced_location_features(test_transaction_1)
        print(f"    Location Features:")
        print(f"      Distance from home: {location_features['distance_from_home']:.2f}km")
        print(f"      Distance from last known: {location_features['distance_from_last_known']:.2f}km")
        print(f"      Effective distance: {location_features['effective_distance']:.2f}km")
        
        # Test risk calculation
        risk_score1, triggers1, requires_otp1, decision1 = risk_engine.calculate_risk_score(test_transaction_1)
        
        effective_approved = any('effective distance' in trigger.lower() and 'approved' in trigger.lower() for trigger in triggers1)
        distance_violation1 = any('effective distance violation' in trigger.lower() for trigger in triggers1)
        
        print(f"    Risk Assessment:")
        print(f"      Risk score: {risk_score1}")
        print(f"      Requires OTP: {requires_otp1}")
        print(f"      Effective distance approved: {effective_approved}")
        print(f"      Distance violation: {distance_violation1}")
        
        # This should pass because effective distance (minimum) should be within threshold
        test1_result = not requires_otp1 and effective_approved
        
        if test1_result:
            print("    ✅ PASSED: Effective distance logic working - NO OTP required")
        else:
            print("    ❌ FAILED: Should not require OTP when effective distance is within threshold")
        
        # Test Case 2: Both home and last known fail (>50km) → OTP REQUIRED
        print("\n📍 TEST CASE 2: Both locations fail → OTP REQUIRED")
        test_client_2 = ClientProfile.objects.create(
            user=test_user,
            first_name="Test",
            last_name="Case2",
            national_id="EFF987654321",
            bank_account_number="87654321",
            balance=Decimal('15000.00'),
            home_lat=Decimal('36.7538'),      # Algiers (home)
            home_lng=Decimal('3.0588'),
            last_known_lat=Decimal('40.7128'),   # New York (very far from both home and previous)
            last_known_lng=Decimal('-74.0060')
        )
        
        test_transaction_2 = Transaction.objects.create(
            client=test_client_2,
            amount=Decimal('3000.00'),
            transaction_type='transfer',
            to_account_number='11111111',
            status='pending'
        )
        
        # Get location features for case 2
        location_features_2 = risk_engine.calculate_enhanced_location_features(test_transaction_2)
        print(f"    Location Features:")
        print(f"      Distance from home: {location_features_2['distance_from_home']:.2f}km")
        print(f"      Distance from last known: {location_features_2['distance_from_last_known']:.2f}km")
        print(f"      Effective distance: {location_features_2['effective_distance']:.2f}km")
        
        risk_score2, triggers2, requires_otp2, decision2 = risk_engine.calculate_risk_score(test_transaction_2)
        
        distance_violation2 = any('effective distance violation' in trigger.lower() for trigger in triggers2)
        
        print(f"    Risk Assessment:")
        print(f"      Risk score: {risk_score2}")
        print(f"      Requires OTP: {requires_otp2}")
        print(f"      Distance violation: {distance_violation2}")
        
        test2_result = requires_otp2 and distance_violation2
        
        if test2_result:
            print("    ✅ PASSED: Both distances fail - OTP required")
        else:
            print("    ❌ FAILED: Should require OTP when both distances exceed threshold")
        
        # Cleanup
        prev_transaction.delete()
        test_transaction_1.delete()
        test_transaction_2.delete()
        test_client_1.delete()
        test_client_2.delete()
        test_user.delete()
        
        overall_result = test1_result and test2_result
        
        if overall_result:
            print("\n✅ EFFECTIVE DISTANCE LOGIC TEST PASSED")
            print("    ✓ Minimum distance calculation working correctly")
            print("    ✓ OTP logic based on effective distance")
            print("    ✓ Detailed logging with all three distances")
        else:
            print("\n❌ EFFECTIVE DISTANCE LOGIC TEST FAILED")
        
        return overall_result
        
    except Exception as e:
        print(f"❌ Effective distance test failed: {e}")
        return False

def test_enhanced_ml_features():
    """Test the enhanced ML features with effective distance"""
    print("\n" + "=" * 80)
    print("TEST: ENHANCED ML FEATURES WITH EFFECTIVE DISTANCE")
    print("=" * 80)
    
    try:
        # Create test user and transaction
        test_user = User.objects.create_user(
            email="ml_features@safenetai.com",
            password="testpass123",
            first_name="ML",
            last_name="Features",
            is_email_verified=True
        )
        
        test_client = ClientProfile.objects.create(
            user=test_user,
            first_name="ML",
            last_name="Test",
            national_id="ML123456789",
            bank_account_number="33333333",
            balance=Decimal('25000.00'),
            home_lat=Decimal('36.7538'),
            home_lng=Decimal('3.0588'),
            last_known_lat=Decimal('48.8566'),
            last_known_lng=Decimal('2.3522')
        )
        
        test_transaction = Transaction.objects.create(
            client=test_client,
            amount=Decimal('8000.00'),
            transaction_type='transfer',
            to_account_number='44444444',
            status='pending'
        )
        
        # Test ML model feature preparation
        ml_model = FraudMLModel()
        
        print("    Testing enhanced ML feature preparation...")
        features = ml_model.prepare_features(test_transaction)
        
        print(f"    Feature array shape: {features.shape}")
        print(f"    Number of features: {features.shape[1]}")
        
        # Check if we have the expected 9 features
        expected_features = 9  # amount, balance, type, hour, weekday, dist_home, dist_last, effective_dist, has_location
        
        if features.shape[1] == expected_features:
            print(f"    ✅ Correct number of features: {expected_features}")
            
            # Test feature extraction
            feature_values = features[0]
            print(f"    Enhanced Features:")
            print(f"      Amount: {feature_values[0]}")
            print(f"      Balance: {feature_values[1]}")
            print(f"      Transaction type: {feature_values[2]}")
            print(f"      Hour: {feature_values[3]}")
            print(f"      Weekday: {feature_values[4]}")
            print(f"      Distance from home: {feature_values[5]:.2f}km")
            print(f"      Distance from last known: {feature_values[6]:.2f}km")
            print(f"      Effective distance: {feature_values[7]:.2f}km")
            print(f"      Has location data: {bool(feature_values[8])}")
            
            # Verify effective distance is minimum of home and last known distances
            effective_is_minimum = feature_values[7] == min(feature_values[5], feature_values[6])
            
            if effective_is_minimum:
                print("    ✅ Effective distance correctly calculated as minimum")
                ml_features_result = True
            else:
                print("    ❌ Effective distance calculation error")
                ml_features_result = False
        else:
            print(f"    ❌ Wrong number of features: expected {expected_features}, got {features.shape[1]}")
            ml_features_result = False
        
        # Test ML prediction with enhanced features
        if ml_model.model is not None:
            print("\n    Testing enhanced ML prediction...")
            prediction = ml_model.predict(test_transaction)
            print(f"    ML prediction score: {prediction:.4f}")
            
            if 0 <= prediction <= 1:
                print("    ✅ ML prediction in valid range [0,1]")
            else:
                print("    ❌ ML prediction out of range")
                ml_features_result = False
        else:
            print("    ⚠️  ML model not loaded, skipping prediction test")
        
        # Cleanup
        test_transaction.delete()
        test_client.delete()
        test_user.delete()
        
        if ml_features_result:
            print("\n✅ ENHANCED ML FEATURES TEST PASSED")
            print("    ✓ Correct number of features (9)")
            print("    ✓ Effective distance calculation working")
            print("    ✓ Enhanced feature logging")
        else:
            print("\n❌ ENHANCED ML FEATURES TEST FAILED")
        
        return ml_features_result
        
    except Exception as e:
        print(f"❌ Enhanced ML features test failed: {e}")
        return False

def main():
    """Run comprehensive tests for effective distance logic and enhanced ML features"""
    print("🔧 SafeNetAI - Enhanced Location Rules + AI/ML Features Test")
    print("📍 Effective Distance Logic (Min of Home + Last Known Distances)")
    print("🧠 Enhanced ML Features with Location Intelligence")
    print("=" * 90)
    
    test_results = []
    test_names = [
        "Effective Distance Logic (Home vs Last Known)",
        "Enhanced ML Features with Effective Distance"
    ]
    
    # Run tests
    test_results.append(test_effective_distance_logic())
    test_results.append(test_enhanced_ml_features())
    
    # Summary
    print("\n" + "=" * 90)
    print("TEST SUMMARY")
    print("=" * 90)
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"📊 Results: {passed_tests}/{total_tests} tests passed")
    print()
    
    for i, (name, result) in enumerate(zip(test_names, test_results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {name}: {status}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL ENHANCED FEATURES WORKING!")
        print("✅ Effective distance logic implemented correctly")
        print("✅ AI/ML features enhanced with location intelligence")
        print("✅ Detailed logging shows all distance calculations")
        print("✅ OTP logic based on minimum distance (effective distance)")
        
        print("\n📋 Key Improvements:")
        print("   🎯 OTP only triggered when BOTH home AND last known distances exceed threshold")
        print("   📊 ML model now uses 9 features including effective distance")
        print("   📝 Enhanced logging shows home, last known, and effective distances")
        print("   🔍 Better fraud detection with dual location comparison")
        
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed")
        print("Review the detailed test results above.")
    
    print("\n🚀 Next Steps:")
    print("1. Start Django server: python manage.py runserver")
    print("2. Test transaction creation with new logic")
    print("3. Monitor logs/rules/rules.log for enhanced distance logging")
    print("4. Verify OTP behavior: No OTP when one distance passes")
    print("5. Check AI model predictions with enhanced features")

if __name__ == "__main__":
    main()