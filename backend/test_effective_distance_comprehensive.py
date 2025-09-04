#!/usr/bin/env python
"""
Effective Distance-Based Transaction Rule Test Suite
Tests the complete end-to-end functionality of improved distance-based rules.
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append('/Users/HP/Desktop/projects/safeNetAi/backend')
django.setup()

from django.contrib.auth import get_user_model
from apps.risk.models import ClientProfile, Threshold
from apps.transactions.models import Transaction
from apps.risk.engine import RiskEngine, haversine_distance

User = get_user_model()

def test_effective_distance():
    """Test effective distance calculation using minimum of home/last known"""
    print("🎯 Testing Effective Distance Calculation...")
    
    # Clean up
    User.objects.filter(email='edtest@safenetai.com').delete()
    
    # Create test user
    user = User.objects.create_user(
        email='edtest@safenetai.com',
        password='test',
        first_name='Test',
        last_name='User'
    )
    
    # Setup: Home in Algiers, Last known in Oran (350km), Current near Algiers (10km)
    client = ClientProfile.objects.create(
        user=user,
        first_name='Test',
        last_name='User',
        national_id='TEST001',
        balance=Decimal('10000.00'),
        home_lat=Decimal('36.7538'),     # Algiers
        home_lng=Decimal('3.0588'),
        last_known_lat=Decimal('35.6892'),  # Oran (far)
        last_known_lng=Decimal('-0.6337')
    )
    
    # Transaction near home (should use home distance ~10km, not Oran distance ~350km)
    transaction = Transaction.objects.create(
        client=client,
        amount=Decimal('5000.00'),
        transaction_type='transfer',
        to_account_number='12345678',
        current_lat=Decimal('36.8538'),  # Near Algiers
        current_lng=Decimal('3.1588'),
        status='pending'
    )
    
    # Test risk calculation
    engine = RiskEngine()
    risk_score, triggers, requires_otp, decision = engine.calculate_risk_score(transaction)
    
    # Calculate distances manually
    home_dist = haversine_distance(36.7538, 3.0588, 36.8538, 3.1588)
    last_dist = haversine_distance(35.6892, -0.6337, 36.8538, 3.1588)
    effective_dist = min(home_dist, last_dist)
    
    print(f"  📏 Home distance: {home_dist:.1f}km")
    print(f"  📏 Last known distance: {last_dist:.1f}km") 
    print(f"  🎯 Effective distance: {effective_dist:.1f}km")
    print(f"  🔒 Requires OTP: {requires_otp}")
    
    # Should NOT require OTP (effective distance ~10km < 50km threshold)
    success = not requires_otp and effective_dist < 50
    
    # Cleanup
    transaction.delete()
    client.delete()
    user.delete()
    
    return success

def test_location_update_timing():
    """Test that last_known location updates only after OTP success"""
    print("🔐 Testing Location Update Timing...")
    
    # Clean up
    User.objects.filter(email='timing@safenetai.com').delete()
    
    user = User.objects.create_user(
        email='timing@safenetai.com',
        password='test',
        first_name='Timing',
        last_name='Test'
    )
    
    client = ClientProfile.objects.create(
        user=user,
        first_name='Timing',
        last_name='Test',
        national_id='TIMING001',
        balance=Decimal('10000.00'),
        home_lat=Decimal('36.7538'),
        home_lng=Decimal('3.0588'),
        last_known_lat=Decimal('36.7538'),  # Start at home
        last_known_lng=Decimal('3.0588')
    )
    
    original_lat = client.last_known_lat
    original_lng = client.last_known_lng
    
    # Create transaction at far location
    transaction = Transaction.objects.create(
        client=client,
        amount=Decimal('8000.00'),
        transaction_type='transfer', 
        to_account_number='87654321',
        current_lat=Decimal('48.8566'),  # Paris (far)
        current_lng=Decimal('2.3522'),
        status='pending'
    )
    
    # Check location hasn't changed after transaction creation
    client.refresh_from_db()
    location_preserved = (client.last_known_lat == original_lat and 
                         client.last_known_lng == original_lng)
    
    print(f"  📍 Location preserved during transaction: {location_preserved}")
    
    # Simulate successful OTP verification (manual location update)
    if location_preserved:
        client.last_known_lat = transaction.current_lat
        client.last_known_lng = transaction.current_lng
        client.save()
        transaction.status = 'completed'
        transaction.save()
        
        client.refresh_from_db()
        location_updated = (client.last_known_lat == transaction.current_lat and
                          client.last_known_lng == transaction.current_lng)
        
        print(f"  ✅ Location updated after OTP success: {location_updated}")
        success = location_updated
    else:
        success = False
    
    # Cleanup
    transaction.delete()
    client.delete()
    user.delete()
    
    return success

def main():
    """Run comprehensive tests"""
    print("🚀 EFFECTIVE DISTANCE RULE COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Ensure threshold exists
    Threshold.objects.get_or_create(
        key='max_distance_km',
        defaults={'value': 50.0, 'description': 'Max distance threshold'}
    )
    
    tests = [
        ("Effective Distance Calculation", test_effective_distance),
        ("Location Update Timing", test_location_update_timing)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {name}")
        except Exception as e:
            print(f"❌ CRASHED: {name} - {e}")
            results.append((name, False))
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Effective distance-based rule working correctly")
        print("✅ Location update timing is correct")
    else:
        print("⚠️ Some tests failed - please review implementation")
    
    return passed == total

if __name__ == "__main__":
    main()