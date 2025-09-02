# SafeNetAi Backend

A Django REST Framework backend for the SafeNetAi fraud detection system, featuring rule-based and machine learning fraud detection, OTP email verification, and comprehensive transaction monitoring.

## ✅ **Current System Status (January 2025)**

### **✓ Critical Issues Resolved:**
- **FraudAlert Creation**: Fixed `message` parameter error in fraud alert generation
- **User Model Tests**: Resolved `role` parameter issues in all test files
- **Transaction Processing**: Fixed serializer field mapping errors
- **AI Model Integration**: Verified Isolation Forest model (1.77MB) is fully functional
- **Email Service**: Confirmed Gmail SMTP integration working properly
- **Environment Variables**: All required settings properly configured and tested

### **✓ System Components Status:**
- **Django Server**: Running on port 8000 without errors ✅
- **Database**: SQLite with all migrations applied ✅
- **AI/ML Model**: Fraud detection operational ✅
- **Email System**: SMTP configured and sending emails ✅
- **Logging System**: 6 categorized log files active ✅
- **OTP Verification**: High-risk transaction verification working ✅

## 🚀 Features

### **Core Security Features**
- **Advanced Fraud Detection**: Combination of rule-based engine + ML anomaly detection
- **Real-time Risk Scoring**: 0-100 scale with configurable thresholds
- **OTP Email Verification**: Automatic OTP for transactions with risk score ≥ 70
- **Comprehensive Logging**: 6 categorized log files with rotation
- **Admin Dashboard**: Complete fraud alert management and system monitoring

### **Authentication & User Management**
- **Custom User Model**: Email-based authentication with OTP verification
- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Role-based Access**: Separate client and admin interfaces
- **Email Verification**: Required OTP verification for account activation

### **Transaction Processing**
- **Multi-type Transactions**: Support for deposits, withdrawals, and transfers
- **Real-time Processing**: Instant risk assessment and routing decisions
- **Balance Management**: Automatic balance updates with rollback on failure
- **Audit Trail**: Complete transaction history with risk scores and alerts

### **AI/ML Integration**
- **Isolation Forest Model**: Scikit-learn based anomaly detection
- **Feature Engineering**: Transaction patterns, user behavior, timing analysis
- **Model Training**: Management commands for model retraining
- **Prediction API**: REST endpoint for real-time fraud prediction

## 🛠️ Technology Stack

- **Django 4.2.7** - Web framework with security features
- **Django REST Framework 3.14.0** - API framework
- **Simple JWT 5.3.0** - JWT authentication
- **scikit-learn 1.3.2** - Machine learning (Isolation Forest)
- **pandas 2.1.4** - Data processing and analysis
- **numpy 1.26.2** - Numerical computations
- **python-dotenv 1.0.0** - Environment variable management
- **SQLite** (development) / **PostgreSQL** (production) - Database
- **Gmail SMTP** - Email service integration

## 📋 Prerequisites

- Python 3.8+
- pip

## 🚀 Quick Start

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the backend directory:
```powershell
# Create .env file
New-Item -Path ".env" -ItemType File
```

Add the following configuration:
```env
# Django Configuration
DEBUG=1
SECRET_KEY=xaUlkckAQwIcC1V3W28duX4cFd1elWsQ

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration (Gmail SMTP)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password

# Site Configuration
SITE_BASE_URL=http://localhost:5173
EMAIL_TOKEN_TTL_HOURS=24
```

**Gmail Setup:**
1. Enable 2-factor authentication on Gmail
2. Generate App Password: Google Account → Security → App passwords
3. Use the 16-character App Password (not your regular password)

### 4. Database Setup
```powershell
# Apply database migrations
python manage.py migrate
```

### 5. Create Superuser
```powershell
python manage.py createsuperuser
# Enter email, first name, last name, and password
```

### 6. Set Up Initial Data
```powershell
# Create default thresholds and rules
python manage.py setup_initial_data

# Generate test data (optional)
python manage.py generate_fake_data --users 10 --transactions 50
```

### 7. Start Development Server
```powershell
python manage.py runserver 8000
```

✅ **The API will be available at**: http://localhost:8000
✅ **Admin interface at**: http://localhost:8000/admin/
✅ **API documentation**: All endpoints accessible via `/api/`

## 📁 Project Structure

```
backend/
├── apps/
│   ├── users/              # User management and authentication
│   │   ├── models.py       # User and EmailOTP models
│   │   ├── views.py        # User viewsets
│   │   ├── serializers.py  # User serializers
│   │   ├── auth_views.py   # Authentication views
│   │   ├── email_service.py # Email functionality
│   │   └── tests/          # User tests
│   ├── risk/               # Risk management and fraud detection
│   │   ├── models.py       # ClientProfile, Rule, Threshold models
│   │   ├── engine.py       # RiskEngine for fraud detection
│   │   ├── ml.py           # Machine learning integration
│   │   ├── views.py        # Risk views
│   │   ├── serializers.py  # Risk serializers
│   │   ├── admin_views.py  # Admin viewsets
│   │   └── management/     # Management commands
│   └── transactions/       # Transaction management
│       ├── models.py       # Transaction and FraudAlert models
│       ├── views.py        # Transaction viewsets
│       ├── serializers.py  # Transaction serializers
│       └── signals.py      # Transaction signals
├── backend/                # Django project settings
│   ├── settings.py         # Django settings
│   ├── urls.py             # URL configuration
│   └── wsgi.py             # WSGI configuration
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django Configuration
DEBUG=1
SECRET_KEY=your-secret-key-change-in-production

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
SITE_BASE_URL=http://localhost:3000
EMAIL_TOKEN_TTL_HOURS=24
```

### Database Configuration

The application supports both SQLite (development) and PostgreSQL (production):

```python
# SQLite (Development)
DATABASE_URL=sqlite:///db.sqlite3

# PostgreSQL (Production)
DATABASE_URL=postgresql://user:password@localhost:5432/safenetai
```

### Email Configuration

For production, configure SMTP settings:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/verify-otp/` - OTP verification
- `POST /api/auth/resend-otp/` - Resend OTP
- `POST /api/auth/refresh/` - Token refresh

### Client Operations
- `GET /api/client/profile/me/` - Get user profile
- `GET /api/client/transactions/` - List user transactions
- `POST /api/client/transactions/` - Create transaction
- `GET /api/client/fraud-alerts/` - List user fraud alerts

### Admin Operations
- `GET /api/admin/clients/` - List all clients
- `POST /api/admin/clients/` - Create client profile
- `GET /api/admin/transactions/` - List all transactions
- `GET /api/admin/fraud-alerts/` - List all fraud alerts
- `PATCH /api/admin/fraud-alerts/{id}/approve/` - Approve alert
- `PATCH /api/admin/fraud-alerts/{id}/reject/` - Reject alert

### AI Operations
- `POST /api/ai/predict/` - ML fraud prediction

## 🔍 **Fraud Detection System**

### **Rule-Based Detection Engine**

The system implements 7 configurable fraud detection rules:

| Rule | Trigger Condition | Risk Points | Description |
|------|------------------|-------------|-------------|
| **Large Amount** | Amount > 10,000 DZD | +30 | Flags high-value transactions |
| **High Frequency** | >5 transactions/hour | +25 | Detects rapid transaction bursts |
| **Low Balance** | Balance < 100 DZD after | +20 | Warns of potential account draining |
| **Location Anomaly** | >50km from last transaction | +20 | Geographic inconsistency detection |
| **Statistical Outlier** | Z-score > 2.0 | +15 | Amount significantly different from user average |
| **Device Change** | Different device fingerprint | +15 | New device detection |
| **Unusual Time** | 23:00-05:00 transactions | +10 | Late night/early morning activity |

### **Machine Learning Integration**

- **Algorithm**: Isolation Forest (scikit-learn)
- **Model File**: `models/fraud_isolation.joblib` (1.77MB)
- **Features**: Amount, time patterns, user behavior, frequency
- **Output**: Anomaly score (0.0 = normal, 1.0 = highly suspicious)
- **Training Data**: Historical transaction patterns and known fraud cases

### **Risk Scoring System**

- **Score Range**: 0-100 (combined rule-based + ML scoring)
- **Risk Levels**: 
  - **Low (0-39)**: Normal processing
  - **Medium (40-69)**: Enhanced monitoring 
  - **High (70-100)**: OTP verification required
- **Decision Actions**: 
  - **Allow**: Automatic processing
  - **Flag for Review**: Admin notification
  - **Block**: Automatic transaction rejection

### **OTP Verification System**

- **Trigger**: Risk score ≥ 70 or admin-defined rules
- **Delivery**: Gmail SMTP with HTML templates
- **Expiration**: 10 minutes from generation
- **Attempts**: Maximum 3 attempts per OTP
- **Security**: Automatic OTP deletion after use

## 🧪 **Testing Instructions**

### **Business Rules Testing**

#### Run All Tests
```powershell
python manage.py test
```

#### Test Specific Components
```powershell
# Test user authentication and OTP
python manage.py test apps.users

# Test fraud detection engine
python manage.py test apps.risk

# Test transaction processing
python manage.py test apps.transactions
```

#### Test Coverage Analysis
```powershell
# Install coverage if needed
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generates htmlcov/ directory with detailed report
```

### **AI Model Testing**

#### Test Fraud Prediction API
```powershell
# Test the ML prediction endpoint
curl -X POST http://localhost:8000/api/ai/predict/ ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_JWT_TOKEN" ^
  -d "{
    'amount': 15000,
    'transaction_type': 'transfer',
    'hour_of_day': 2,
    'day_of_week': 6
  }"
```

#### Expected AI Outputs
- **Normal Transaction** (score 0.0-0.3): Low risk, proceed normally
- **Suspicious Transaction** (score 0.3-0.6): Medium risk, monitor closely  
- **Fraudulent Transaction** (score 0.6-1.0): High risk, require OTP/block

### **Email Service Testing**

#### Test SMTP Configuration
```powershell
# Create test script to verify email config
python test_email_config.py
```

#### Test OTP Email Delivery
```powershell
# Register new user to test OTP email
# High-risk transaction to test transaction OTP
# Check Gmail for delivered emails
```

### **Rule Engine Testing**

Test individual fraud detection rules:

```powershell
# Create transaction data that triggers specific rules
python manage.py shell
```

```python
# In Django shell
from apps.risk.engine import RiskEngine
from apps.transactions.models import Transaction
from apps.risk.models import ClientProfile

# Test large amount rule (>10,000 DZD)
engine = RiskEngine()
client = ClientProfile.objects.first()
transaction = Transaction(
    client=client,
    amount=15000,  # Triggers large amount rule
    transaction_type='transfer'
)
risk_score, triggers, requires_otp, decision = engine.calculate_risk_score(transaction)
print(f"Risk Score: {risk_score}, Triggers: {triggers}")
```

## 🏗️ Management Commands

### Setup Initial Data
```bash
python manage.py setup_initial_data
```

### Train Fraud Model
```bash
python manage.py train_fraud_model
```

### Create Superuser
```bash
python manage.py createsuperuser
```

## 🔒 **Security Features**

### **Authentication Security**
- **JWT Authentication**: Secure token-based auth with 12-hour access tokens
- **Refresh Tokens**: 7-day refresh token rotation
- **Email Verification**: Mandatory OTP verification for account activation
- **Password Security**: Django's built-in password validation

### **Transaction Security**
- **Real-time Risk Assessment**: Every transaction gets risk scoring
- **OTP Verification**: Automatic OTP for high-risk transactions (score ≥ 70)
- **Balance Validation**: Prevents overdrafts and negative balances
- **Audit Trail**: Complete transaction logging with risk details

### **System Security**
- **Input Validation**: Comprehensive form and API validation
- **CORS Configuration**: Proper cross-origin resource sharing
- **Environment Variables**: Secure configuration management
- **Rate Limiting**: OTP resend and API request rate limiting
- **SQL Injection Protection**: Django ORM built-in protection
- **XSS Protection**: Content security policy implementation

## 📊 **Admin Interface**

✅ **Access**: http://localhost:8000/admin (login with superuser credentials)

### **Available Management Modules**

| Module | Description | Key Features |
|--------|-------------|---------------|
| **Users** | User account management | Email verification, role assignment, profile linking |
| **Client Profiles** | Client profile management | Balance updates, transaction history, risk scores |
| **Transactions** | Transaction monitoring | Real-time status, risk scores, OTP tracking |
| **Fraud Alerts** | Alert management | Risk assessment, approve/reject actions, status tracking |
| **Rules** | Detection rule configuration | Enable/disable rules, description management |
| **Thresholds** | Risk threshold settings | Configurable values for all fraud detection rules |
| **Email OTPs** | OTP management | View active OTPs, usage tracking, expiration monitoring |

### **Dashboard Features**
- **Real-time Statistics**: Transaction counts, fraud alert summaries
- **System Health**: Database status, email service status
- **Log Monitoring**: Access to all 6 categorized log files
- **User Activity**: Login tracking, registration monitoring

## 🚀 Deployment

### Production Settings

1. **Environment Variables**:
   ```env
   DEBUG=0
   SECRET_KEY=your-production-secret-key
   DATABASE_URL=postgresql://user:password@localhost:5432/safenetai
   ```

2. **Static Files**:
   ```bash
   python manage.py collectstatic
   ```

3. **Database Migration**:
   ```bash
   python manage.py migrate
   ```

4. **WSGI Server**:
   ```bash
   gunicorn backend.wsgi:application
   ```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 🔧 Development

### Available Commands

```bash
# Development
python manage.py runserver          # Start development server
python manage.py makemigrations     # Create migrations
python manage.py migrate            # Apply migrations
python manage.py shell              # Django shell

# Testing
python manage.py test               # Run tests
python manage.py test --verbosity=2 # Verbose test output

# Management
python manage.py createsuperuser    # Create admin user
python manage.py setup_initial_data # Setup initial data
python manage.py train_fraud_model  # Train ML model
```

### Code Style

The project follows:
- **PEP 8** for Python code style
- **Django coding style** for Django-specific code
- **Type hints** for better code documentation

## 🐛 Troubleshooting

### Common Issues

1. **Database Errors**
   - Run `python manage.py migrate`
   - Check database connection settings
   - Verify database permissions

2. **Email Issues**
   - Check email configuration in `.env`
   - Verify SMTP credentials
   - Test email settings in Django shell

3. **Authentication Issues**
   - Check JWT settings
   - Verify token expiration
   - Check CORS configuration

4. **ML Model Issues**
   - Install scikit-learn: `pip install scikit-learn`
   - Run model training: `python manage.py train_fraud_model`
   - Check model file permissions

## 🤝 Contributing

1. Follow Django coding conventions
2. Add tests for new features
3. Update documentation
4. Test thoroughly before submitting

## 📝 License

This project is licensed under the MIT License.
