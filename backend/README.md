# SafeNetAi Backend

A Django REST Framework backend for the SafeNetAi fraud detection system, featuring rule-based and machine learning fraud detection, OTP email verification, and admin-first client onboarding.

## 🚀 Features

- **Custom User Model**: Email-based authentication with OTP verification
- **Admin-First Client Onboarding**: Admins create client profiles, users register with matching credentials
- **Fraud Detection Engine**: Rule-based + ML-powered risk scoring
- **Transaction Management**: Real-time fraud detection on transactions
- **Email Notifications**: OTP verification and fraud alert emails
- **JWT Authentication**: Secure token-based authentication
- **Admin Panel**: Complete admin interface for system management
- **Machine Learning Integration**: Isolation Forest for anomaly detection

## 🛠️ Technology Stack

- **Django 5.2** - Web framework
- **Django REST Framework** - API framework
- **Simple JWT** - Authentication
- **scikit-learn** - Machine learning
- **pandas/numpy** - Data processing
- **SQLite/PostgreSQL** - Database
- **python-dotenv** - Environment management

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
```env
DEBUG=1
SECRET_KEY=your-secret-key-change-in-production
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
SITE_BASE_URL=http://localhost:3000
EMAIL_TOKEN_TTL_HOURS=24
DATABASE_URL=sqlite:///db.sqlite3
```

### 4. Database Setup
```bash
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Set Up Initial Data
```bash
python manage.py setup_initial_data
```

### 7. Start Development Server
```bash
python manage.py runserver
```

The API will be available at http://localhost:8000

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

## 🔍 Fraud Detection

### Rule-Based Detection

The system includes several configurable rules:

1. **Large Withdrawal Detection**: Flags transactions above threshold
2. **High Frequency Monitoring**: Detects unusual transaction frequency
3. **Low Balance Alerts**: Warns when balance drops below threshold
4. **Location Anomaly**: Detects transactions from unusual locations
5. **Statistical Outlier**: Identifies transactions outside normal patterns

### Machine Learning Integration

- **Isolation Forest**: Anomaly detection algorithm
- **Feature Engineering**: Transaction and user behavior features
- **Model Training**: Management command for model training
- **Real-time Prediction**: Live fraud scoring

### Risk Scoring

- **Score Range**: 0-100
- **Risk Levels**: Low (0-39), Medium (40-69), High (70-100)
- **Actions**: Automatic blocking, OTP requirement, or monitoring

## 🧪 Testing

### Run All Tests
```bash
python manage.py test
```

### Run Specific App Tests
```bash
python manage.py test apps.users
python manage.py test apps.risk
python manage.py test apps.transactions
```

### Run with Coverage
```bash
coverage run --source='.' manage.py test
coverage report
coverage html
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

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Email Verification**: OTP-based email verification
- **Rate Limiting**: OTP resend rate limiting
- **Input Validation**: Comprehensive form validation
- **CORS Configuration**: Proper cross-origin resource sharing
- **Environment Variables**: Secure configuration management

## 📊 Admin Interface

Access the admin interface at http://localhost:8000/admin

### Available Models

- **Users**: User management and email verification
- **Client Profiles**: Client profile management
- **Transactions**: Transaction monitoring
- **Fraud Alerts**: Fraud alert management
- **Rules**: Fraud detection rule configuration
- **Thresholds**: Risk threshold configuration

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
