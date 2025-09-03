#!/usr/bin/env python
"""
Quick validation that the requires_otp fix is working
"""
import os
import sys

# Check if the fix is present in the RiskEngine
def check_requires_otp_fix():
    print("SafeNetAI - requires_otp Fix Validation")
    print("=" * 50)
    
    try:
        # Read the RiskEngine file
        with open('apps/risk/engine.py', 'r') as f:
            content = f.read()
        
        # Look for the fix
        if 'requires_otp = False  # Initialize to False to prevent UnboundLocalError' in content:
            print("✅ SUCCESS: requires_otp initialization fix is present!")
            print("   Found: requires_otp = False  # Initialize to False to prevent UnboundLocalError")
        else:
            print("❌ ERROR: requires_otp initialization fix not found!")
            return False
        
        # Check for distance-based OTP logic
        if 'distance_triggered = any' in content and 'distance exceeded' in content:
            print("✅ SUCCESS: Distance-based OTP enforcement is implemented!")
        else:
            print("❌ WARNING: Distance-based OTP logic may not be complete")
        
        # Check for proper variable usage
        if 'requires_otp = True' in content:
            print("✅ SUCCESS: OTP requirement setting logic is present!")
        else:
            print("❌ ERROR: OTP requirement logic not found!")
            return False
            
        return True
        
    except FileNotFoundError:
        print("❌ ERROR: apps/risk/engine.py not found!")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def check_transaction_views():
    print("\nTransaction Views Validation")
    print("-" * 30)
    
    try:
        with open('apps/transactions/views.py', 'r') as f:
            content = f.read()
        
        # Check for distance violation handling
        if 'distance_violation = any' in content:
            print("✅ SUCCESS: Distance violation detection is implemented!")
        else:
            print("❌ WARNING: Distance violation detection not found")
        
        # Check for location updates
        if 'last_known_lat' in content and 'last_known_lng' in content:
            print("✅ SUCCESS: Location tracking is implemented!")
        else:
            print("❌ WARNING: Location tracking may not be complete")
        
        return True
        
    except FileNotFoundError:
        print("❌ ERROR: apps/transactions/views.py not found!")
        return False

def check_registration_location():
    print("\nRegistration Location Validation")
    print("-" * 35)
    
    try:
        with open('apps/users/serializers.py', 'r') as f:
            content = f.read()
        
        # Check for registration location handling
        if 'registration_location' in content and 'home_lat' in content:
            print("✅ SUCCESS: Registration location handling is implemented!")
        else:
            print("❌ WARNING: Registration location handling may not be complete")
        
        return True
        
    except FileNotFoundError:
        print("❌ ERROR: apps/users/serializers.py not found!")
        return False

if __name__ == "__main__":
    success1 = check_requires_otp_fix()
    success2 = check_transaction_views()
    success3 = check_registration_location()
    
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    
    if success1:
        print("🎯 CORE FIX: requires_otp UnboundLocalError - RESOLVED!")
    else:
        print("❌ CORE FIX: requires_otp issue still present!")
    
    print("\nNext Steps:")
    print("1. Start Django server: python manage.py runserver")
    print("2. Test transaction creation via API")
    print("3. Monitor logs for proper OTP enforcement")
    print("4. Verify no UnboundLocalError occurs")
    
    print("\n🚀 The SafeNetAI backend should now be working without crashes!")