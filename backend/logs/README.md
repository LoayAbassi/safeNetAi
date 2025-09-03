# SafeNetAI - Organized Logging Structure

This directory contains all system logs organized into categorized folders for easy tracing and maintenance.

## 📁 Log Directory Structure

```
logs/
├── auth/           # Authentication & User Management Logs
│   └── auth.log    # Login, logout, registration, OTP verification
├── ai/             # AI/ML Model & Prediction Logs  
│   └── ai.log      # Model training, predictions, feature preparation
├── rules/          # Risk Engine & Rule Evaluation Logs
│   └── rules.log   # Fraud detection rules, risk scoring, thresholds
├── transactions/   # Transaction Processing Logs
│   └── transactions.log # Transaction creation, processing, completion
├── system/         # General System & Django Logs
│   └── system.log  # Django framework, database, general system events
├── errors/         # Error & Exception Logs
│   └── errors.log  # All system errors and critical issues
└── email/          # Email Service & Notification Logs
    └── email.log   # OTP emails, notifications, SMTP operations
```

## 📊 Log Features

- **Daily Rotation**: New log file created each midnight
- **7-Day Retention**: Automatic cleanup keeps last 7 days
- **UTF-8 Encoding**: Proper handling of international characters
- **Detailed Format**: `[timestamp] [level] [module] message`
- **Environment Configuration**: Log levels configurable via `.env`

## 🔍 Log Levels

- **DEBUG**: Detailed debugging information
- **INFO**: General operational messages  
- **WARNING**: Warning conditions
- **ERROR**: Error conditions
- **CRITICAL**: Critical error conditions

## 📋 Usage Examples

### View Recent Authentication Logs
```bash
tail -f logs/auth/auth.log
```

### Search for Transaction Errors
```bash
grep "ERROR" logs/transactions/transactions.log
```

### Monitor AI Model Predictions
```bash
tail -f logs/ai/ai.log | grep "Prediction"
```

### View All Error Logs
```bash
tail -f logs/errors/errors.log
```

## ⚙️ Configuration

Log levels can be configured in `.env`:
```env
LOG_LEVEL_AUTH=INFO
LOG_LEVEL_AI=INFO  
LOG_LEVEL_RULES=INFO
LOG_LEVEL_TRANSACTIONS=INFO
LOG_LEVEL_SYSTEM=INFO
LOG_LEVEL_EMAIL=INFO
```

## 🛡️ Security Notes

- Sensitive data (passwords, tokens) is automatically redacted
- PII is logged appropriately for audit trails
- Access to logs should be restricted to authorized personnel
- Logs contain transaction IDs but not full account details

---

**Generated**: January 2025 | **SafeNetAI** Fraud Detection System