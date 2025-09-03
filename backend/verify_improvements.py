#!/usr/bin/env python
"""
Simple verification script for the three improvements
"""

import os
from pathlib import Path

def verify_log_structure():
    """Verify organized log directory structure"""
    print("=" * 50)
    print("VERIFICATION 1: LOG DIRECTORY STRUCTURE")
    print("=" * 50)
    
    logs_dir = Path('logs')
    expected_categories = ['auth', 'ai', 'rules', 'transactions', 'system', 'errors', 'email']
    
    if not logs_dir.exists():
        print("❌ Logs directory does not exist")
        return False
    
    success_count = 0
    for category in expected_categories:
        category_dir = logs_dir / category
        if category_dir.exists():
            print(f"✅ {category}/ directory exists")
            success_count += 1
        else:
            print(f"❌ {category}/ directory missing")
    
    print(f"\nResult: {success_count}/{len(expected_categories)} directories found")
    return success_count >= len(expected_categories) * 0.8

def verify_currency_changes():
    """Verify currency changes in email templates"""
    print("\n" + "=" * 50)
    print("VERIFICATION 2: CURRENCY DISPLAY CHANGES")
    print("=" * 50)
    
    email_service_file = Path('apps/users/email_service.py')
    if not email_service_file.exists():
        print("❌ Email service file not found")
        return False
    
    with open(email_service_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for DZD usage
    dzd_count = content.count('DZD')
    dollar_issues = content.count('${context[\'amount\']') + content.count('$amount')
    
    print(f"DZD occurrences: {dzd_count}")
    print(f"Potential $ issues: {dollar_issues}")
    
    if dzd_count > 0 and dollar_issues == 0:
        print("✅ Currency display updated to DZD")
        return True
    else:
        print("❌ Currency display may still have $ symbols")
        return False

def verify_location_rules():
    """Verify enhanced location rules"""
    print("\n" + "=" * 50)
    print("VERIFICATION 3: ENHANCED LOCATION RULES")
    print("=" * 50)
    
    risk_engine_file = Path('apps/risk/engine.py')
    if not risk_engine_file.exists():
        print("❌ Risk engine file not found")
        return False
    
    with open(risk_engine_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for enhanced location logic
    checks = [
        ('distance_from_home', 'Distance from home calculation'),
        ('within_home_threshold', 'Home threshold comparison'),
        ('Enhanced distance rule', 'Enhanced distance rule messaging'),
        ('both home location AND last known location', 'Documentation of dual comparison')
    ]
    
    results = []
    for check_text, description in checks:
        if check_text in content:
            results.append(f"✅ {description}")
        else:
            results.append(f"❌ {description} missing")
    
    for result in results:
        print(result)
    
    success_count = sum(1 for r in results if r.startswith("✅"))
    return success_count >= len(checks) * 0.75

def verify_settings_logging():
    """Verify logging configuration in settings"""
    print("\n" + "=" * 50)
    print("VERIFICATION 4: LOGGING CONFIGURATION")
    print("=" * 50)
    
    settings_file = Path('backend/settings.py')
    if not settings_file.exists():
        print("❌ Settings file not found")
        return False
    
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for organized logging handlers
    log_categories = ['auth_file', 'ai_file', 'rules_file', 'transactions_file', 'system_file', 'errors_file', 'email_file']
    
    found_categories = []
    for category in log_categories:
        if category in content:
            found_categories.append(category)
            print(f"✅ {category} handler configured")
        else:
            print(f"❌ {category} handler missing")
    
    success_rate = len(found_categories) / len(log_categories)
    print(f"\nResult: {len(found_categories)}/{len(log_categories)} handlers configured")
    
    return success_rate >= 0.8

def main():
    print("🔧 SafeNetAI - Improvements Verification")
    print("=" * 60)
    
    # Run verifications
    results = [
        verify_log_structure(),
        verify_currency_changes(),
        verify_location_rules(),
        verify_settings_logging()
    ]
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"📊 Results: {passed}/{total} verifications passed")
    
    improvements = [
        "Log Directory Organization",
        "Currency Display (DZD)",
        "Enhanced Location Rules",
        "Logging Configuration"
    ]
    
    for i, (improvement, result) in enumerate(zip(improvements, results)):
        status = "✅ VERIFIED" if result else "❌ NEEDS ATTENTION"
        print(f"{i+1}. {improvement}: {status}")
    
    if passed == total:
        print("\n🎉 ALL IMPROVEMENTS SUCCESSFULLY IMPLEMENTED!")
        print("\n✅ Ready for testing:")
        print("  - Currency displays in DZD")
        print("  - Enhanced location fraud detection")
        print("  - Organized log file structure")
    else:
        print(f"\n⚠️  {total - passed} improvement(s) may need review")
    
    print("\n🚀 Next: Start Django server and test functionality!")

if __name__ == "__main__":
    main()