# SafeNetAI - Comprehensive Testing Guide

## 🎯 **Testing Overview**

This guide provides comprehensive testing instructions for SafeNetAI's business rules, AI outputs, and system integration. Follow these tests to verify all fraud detection capabilities and system functionality.

## 📋 **Prerequisites**

- ✅ SafeNetAI system fully setup and running
- ✅ Backend server on port 8000
- ✅ Frontend server on port 5173  
- ✅ Test data generated (`python manage.py generate_fake_data --users 10 --transactions 50`)
- ✅ Admin account created and accessible

## 🧪 **Business Rules Testing**

### **Rule 1: Large Amount Detection**

**Objective**: Test transactions above threshold trigger high risk scores

```powershell
# Test Setup
cd backend
python manage.py shell
```

```python
# In Django shell - Test Large Amount Rule
from apps.risk.engine import RiskEngine
from apps.transactions.models import Transaction
from apps.risk.models import ClientProfile

# Get test client
client = ClientProfile.objects.first()
engine = RiskEngine()

# Test 1: Normal Amount (should be low risk)
normal_transaction = Transaction(
    client=client,
    amount=5000,  # Below 10,000 threshold
    transaction_type='transfer'
)
risk_score, triggers, requires_otp, decision = engine.calculate_risk_score(normal_transaction)
print(f"Normal Amount - Risk Score: {risk_score}, Triggers: {triggers}")
# Expected: Risk score < 30, no large amount trigger

# Test 2: Large Amount (should trigger rule)
large_transaction = Transaction(
    client=client,
    amount=15000,  # Above 10,000 threshold
    transaction_type='transfer'
)
risk_score, triggers, requires_otp, decision = engine.calculate_risk_score(large_transaction)
print(f"Large Amount - Risk Score: {risk_score}, Triggers: {triggers}")
# Expected: Risk score >= 30, "Large transfer" in triggers
```

**✅ Expected Results**:
- Normal amount (≤10,000 DZD): No large amount trigger
- Large amount (>10,000 DZD): +30 risk points, "Large transfer" trigger

### **Rule 2: High Frequency Detection**

```python
# Test High Frequency Rule
from django.utils import timezone
from datetime import timedelta

# Create multiple transactions for same client
client = ClientProfile.objects.first()

# Test setup: Create 6 transactions in last hour (threshold is 5)
base_time = timezone.now()
for i in range(6):
    Transaction.objects.create(
        client=client,
        amount=1000,
        transaction_type='transfer',
        to_account_number='87654321',
        created_at=base_time - timedelta(minutes=i*5)  # 5 minutes apart
    )

# Test new transaction (should trigger high frequency)
test_transaction = Transaction(
    client=client,
    amount=2000,
    transaction_type='transfer'
)
risk_score, triggers, requires_otp, decision = engine.calculate_risk_score(test_transaction)
print(f"High Frequency - Risk Score: {risk_score}, Triggers: {triggers}")
# Expected: Risk score includes +25, "High frequency" in triggers
```

**✅ Expected Results**:
- ≤5 transactions/hour: No frequency trigger
- >5 transactions/hour: +25 risk points, "High frequency" trigger

### **Rule 3: Low Balance Detection**

```python
# Test Low Balance Rule
client = ClientProfile.objects.first()
client.balance = 500  # Set low balance
client.save()

# Test transaction that would leave balance < 100
low_balance_transaction = Transaction(
    client=client,
    amount=450,  # Leaves 50 DZD (below 100 threshold)
    transaction_type='transfer'
)
risk_score, triggers, requires_otp, decision = engine.calculate_risk_score(low_balance_transaction)
print(f"Low Balance - Risk Score: {risk_score}, Triggers: {triggers}")
# Expected: Risk score includes +20, "Low balance after transaction" in triggers
```

**✅ Expected Results**:
- Balance after transaction ≥100 DZD: No low balance trigger
- Balance after transaction <100 DZD: +20 risk points, "Low balance" trigger

### **Rule 4: Statistical Outlier Detection**

```python
# Test Statistical Outlier Rule
import statistics

# Set client's transaction history for statistical analysis
client = ClientProfile.objects.first()
amounts = [1000, 1200, 950, 1100, 1050]  # Normal amounts
client.avg_amount = statistics.mean(amounts)
client.std_amount = statistics.stdev(amounts)
client.save()

# Test outlier transaction
outlier_transaction = Transaction(
    client=client,
    amount=5000,  # Significantly different from avg ~1060
    transaction_type='transfer'
)
risk_score, triggers, requires_otp, decision = engine.calculate_risk_score(outlier_transaction)
print(f"Statistical Outlier - Risk Score: {risk_score}, Triggers: {triggers}")
# Expected: Risk score includes +15, "Statistical outlier" in triggers
```

**✅ Expected Results**:
- Z-score ≤2.0: No outlier trigger
- Z-score >2.0: +15 risk points, "Statistical outlier" trigger

### **Rule 5: Unusual Time Detection**

```python
# Test Unusual Time Rule
from datetime import datetime

# Mock transaction at unusual time (2:00 AM)
unusual_time_transaction = Transaction(
    client=client,
    amount=3000,
    transaction_type='transfer'
)
# Manually set time to 2:00 AM
unusual_time_transaction.created_at = datetime.now().replace(hour=2)

risk_score, triggers, requires_otp, decision = engine.calculate_risk_score(unusual_time_transaction)
print(f"Unusual Time - Risk Score: {risk_score}, Triggers: {triggers}")
# Expected: Risk score includes +10, "Unusual time" in triggers
```

**✅ Expected Results**:
- Normal hours (6:00-22:59): No unusual time trigger
- Unusual hours (23:00-05:59): +10 risk points, "Unusual time" trigger

### **Rule 6: Device Fingerprint Mismatch**

```python
# Test Device Fingerprint Rule
client = ClientProfile.objects.first()
client.device_fingerprint = "known_device_12345"
client.save()

# Test transaction with different device
device_mismatch_transaction = Transaction(
    client=client,
    amount=2000,
    transaction_type='transfer',
    device_fingerprint="unknown_device_67890"
)
risk_score, triggers, requires_otp, decision = engine.calculate_risk_score(device_mismatch_transaction)
print(f"Device Mismatch - Risk Score: {risk_score}, Triggers: {triggers}")
# Expected: Risk score includes +15, "Device fingerprint mismatch" in triggers
```

**✅ Expected Results**:
- Same device fingerprint: No device trigger
- Different device fingerprint: +15 risk points, "Device fingerprint mismatch" trigger

## 🤖 **AI Model Testing**

### **Test AI Prediction API**

```powershell
# Test AI fraud prediction endpoint
curl -X POST http://localhost:8000/api/ai/predict/ ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_JWT_TOKEN" ^
  -d "{
    \"amount\": 15000,
    \"transaction_type\": \"transfer\",
    \"hour_of_day\": 2,
    \"day_of_week\": 6,
    \"client_id\": 1
  }"
```

**✅ Expected AI Outputs**:

| Scenario | Input | Expected Output | Risk Level |
|----------|-------|----------------|------------|
| Normal Transaction | Amount: 2000, Hour: 14, Day: 2 | 0.0 - 0.3 | Low Risk |
| Suspicious Pattern | Amount: 8000, Hour: 23, Day: 6 | 0.3 - 0.6 | Medium Risk |  
| Highly Suspicious | Amount: 25000, Hour: 3, Day: 0 | 0.6 - 1.0 | High Risk |

### **Test AI Model Integration**

```python
# Test AI model file and integration
import joblib
import os

# Verify model file exists
model_path = "models/fraud_isolation.joblib"
if os.path.exists(model_path):
    print(f"✅ AI model found: {os.path.getsize(model_path) / (1024*1024):.2f} MB")
else:
    print("❌ AI model file not found")

# Load and test model
try:
    model = joblib.load(model_path)
    print("✅ AI model loaded successfully")
    
    # Test prediction with sample data
    import numpy as np
    sample_data = np.array([[15000, 2, 6, 1]])  # amount, hour, day, client_id
    prediction = model.predict(sample_data)
    print(f"✅ AI prediction: {prediction[0]:.3f}")
except Exception as e:
    print(f"❌ AI model error: {e}")
```

**✅ Expected Results**:
- Model file: 1.77MB fraud_isolation.joblib exists
- Model loads without errors
- Predictions return values between 0.0 and 1.0
- Higher risk scenarios return higher scores

## 📧 **Email Service Testing**

### **Test SMTP Configuration**

```powershell
# Test email configuration
cd backend
python test_email_config.py
```

**Expected Output**:
```
✅ Email configuration loaded successfully
✅ SMTP connection established
✅ Test email sent successfully
```

### **Test OTP Email Delivery**

```python
# Test OTP generation and email delivery
from apps.users.models import User, EmailOTP
from apps.users.email_service import send_otp_email

# Get test user
user = User.objects.first()

# Generate and send OTP
otp_instance = EmailOTP.objects.create(
    user=user,
    otp="123456",
    expires_at=timezone.now() + timedelta(minutes=10)
)

# Test email sending
try:
    send_otp_email(user.email, "123456")
    print("✅ OTP email sent successfully")
except Exception as e:
    print(f"❌ Email sending failed: {e}")
```

### **Test Transaction OTP Flow**

```powershell
# Test high-risk transaction OTP requirement
cd frontend
# Navigate to http://localhost:5173
# 1. Login as regular user
# 2. Create transaction with amount > 10,000 DZD
# 3. Verify OTP modal appears
# 4. Check email for OTP code
# 5. Enter OTP and complete transaction
```

**✅ Expected Results**:
- High-risk transactions (score ≥70) trigger OTP requirement
- OTP email delivers within 30 seconds
- OTP modal appears with countdown timer
- Valid OTP completes transaction
- Invalid OTP shows error message

## 🔄 **Integration Testing**

### **End-to-End Transaction Flow**

**Test Case 1: Normal Transaction**
```
1. User Login → 2. Create Transaction (Amount: 5000) → 3. Risk Assessment → 4. Direct Completion
Expected: Risk score < 70, no OTP required, transaction completes immediately
```

**Test Case 2: High-Risk Transaction**
```
1. User Login → 2. Create Transaction (Amount: 15000) → 3. Risk Assessment → 4. OTP Required → 5. Email Delivery → 6. OTP Verification → 7. Completion
Expected: Risk score ≥ 70, OTP modal appears, email sent, verification required
```

**Test Case 3: Admin Fraud Alert Management**
```
1. High-risk transaction created → 2. Fraud alert generated → 3. Admin notification → 4. Admin review → 5. Approve/Reject → 6. User notification
Expected: Alert appears in admin dashboard, admin can approve/reject, user receives notification
```

### **Load Testing**

```python
# Test concurrent transactions
import threading
from concurrent.futures import ThreadPoolExecutor

def create_test_transaction():
    # Simulate transaction creation
    client = ClientProfile.objects.first()
    transaction = Transaction.objects.create(
        client=client,
        amount=5000,
        transaction_type='transfer',
        to_account_number='87654321'
    )
    return transaction.id

# Test 10 concurrent transactions
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(create_test_transaction) for _ in range(10)]
    results = [future.result() for future in futures]

print(f"✅ Created {len(results)} concurrent transactions")
```

## 📊 **Performance Testing**

### **Response Time Testing**

```python
import time

# Test risk engine performance
start_time = time.time()
risk_score, triggers, requires_otp, decision = engine.calculate_risk_score(test_transaction)
processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds

print(f"Risk Engine Processing Time: {processing_time:.2f} ms")
# Expected: < 50ms average
```

### **Database Performance**

```python
from django.db import connection
from django.test.utils import override_settings

# Test query performance
with override_settings(DEBUG=True):
    # Clear previous queries
    connection.queries_log.clear()
    
    # Perform risk assessment
    engine.calculate_risk_score(test_transaction)
    
    # Check query count
    query_count = len(connection.queries)
    print(f"Database Queries: {query_count}")
    # Expected: < 10 queries for risk assessment
```

## ✅ **Test Results Verification**

### **Business Rules Checklist**
- [ ] Large Amount Rule: +30 points for amounts >10,000 DZD
- [ ] High Frequency Rule: +25 points for >5 transactions/hour  
- [ ] Low Balance Rule: +20 points for balance <100 DZD after transaction
- [ ] Statistical Outlier Rule: +15 points for z-score >2.0
- [ ] Unusual Time Rule: +10 points for 23:00-05:59 transactions
- [ ] Device Mismatch Rule: +15 points for different device fingerprint

### **AI Model Checklist**
- [ ] Model file exists (1.77MB fraud_isolation.joblib)
- [ ] Model loads without errors
- [ ] Predictions return 0.0-1.0 range
- [ ] Higher risk scenarios return higher scores
- [ ] API endpoint responds correctly

### **Email System Checklist**
- [ ] SMTP configuration working
- [ ] OTP emails deliver within 30 seconds
- [ ] HTML templates render correctly
- [ ] Email content includes all required information

### **Integration Checklist**
- [ ] Normal transactions complete without OTP
- [ ] High-risk transactions require OTP verification
- [ ] Fraud alerts generate for suspicious transactions
- [ ] Admin can review and manage alerts
- [ ] System logs record all activities

## 🐛 **Test Troubleshooting**

### **Common Test Issues**

**Issue**: Risk engine not calculating correctly
```python
# Debug: Check threshold values
from apps.risk.models import Threshold
thresholds = Threshold.objects.all()
for threshold in thresholds:
    print(f"{threshold.key}: {threshold.value}")
```

**Issue**: AI model not loading
```powershell
# Retrain model if corrupted
python manage.py train_fraud_model
```

**Issue**: OTP emails not sending
```python
# Test email settings
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

**Issue**: Test data not generating properly
```powershell
# Clear and regenerate test data
python manage.py generate_fake_data --users 10 --transactions 50 --clear
```

## 📈 **Performance Benchmarks**

After testing, verify these performance metrics:

| Component | Expected Performance | Test Result |
|-----------|---------------------|-------------|
| Risk Engine | < 50ms per assessment | _____ ms |
| AI Prediction | < 100ms per prediction | _____ ms |
| Email Delivery | < 30 seconds | _____ seconds |
| Database Queries | < 10 queries per assessment | _____ queries |
| API Response | < 200ms average | _____ ms |

## 🎯 **Conclusion**

Upon successful completion of all tests:

✅ **Business Rules**: All 6 fraud detection rules working correctly  
✅ **AI Integration**: Machine learning model operational and accurate  
✅ **Email System**: OTP delivery and notifications functional  
✅ **Integration**: End-to-end workflows complete successfully  
✅ **Performance**: All components meeting benchmark requirements  

**SafeNetAI fraud detection system is fully tested and production-ready.**