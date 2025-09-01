# SafeNetAi - AI-Powered Fraud Detection System

A comprehensive banking security platform that combines rule-based risk assessment with machine learning to detect and prevent fraudulent transactions in real-time.

## 🚀 Features

### Core Security Features
- **AI-Powered Fraud Detection**: Machine learning models analyze transaction patterns
- **Rule-Based Risk Engine**: Configurable rules for transaction monitoring
- **Real-time Risk Scoring**: Instant risk assessment for all transactions
- **OTP Verification**: Email-based verification for high-risk transactions
- **Multi-factor Authentication**: Enhanced security with email verification

### User Management
- **Role-based Access**: Separate interfaces for clients and administrators
- **User Registration**: Email verification with OTP
- **Profile Management**: Complete client profile management
- **Balance Tracking**: Real-time account balance monitoring

### Transaction Management
- **Multiple Transaction Types**: Deposit, withdrawal, and transfer operations
- **Risk-based Processing**: Automatic risk assessment and routing
- **Fraud Alerts**: Real-time notifications for suspicious activities
- **Transaction History**: Complete audit trail with risk scores

### Admin Features
- **Dashboard Analytics**: Real-time system statistics and monitoring
- **User Management**: Complete client account management
- **Fraud Alert Management**: Review and action on security alerts
- **Rule Configuration**: Dynamic threshold and rule management
- **System Logs**: Comprehensive logging with categorized log files
- **AI/ML Reports**: Machine learning model performance metrics

### Email Notifications
- **Rich HTML Emails**: Branded transaction notifications
- **Security Alerts**: Fraud detection notifications
- **OTP Delivery**: Secure verification code delivery
- **Transaction Status Updates**: Real-time transaction notifications

### Logging & Monitoring
- **Categorized Logging**: Separate log files for different modules
- **Log Rotation**: Automatic daily rotation with 7-day retention
- **Admin Log Viewer**: Web-based log monitoring interface
- **System Health Monitoring**: Real-time system status tracking

## 🛠️ Technology Stack

### Backend
- **Django 4.2**: Python web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Primary database
- **Redis**: Caching and session management
- **Celery**: Background task processing
- **Scikit-learn**: Machine learning models
- **JWT**: Authentication tokens

### Frontend
- **React 18**: Modern UI framework
- **Vite**: Fast build tool
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Smooth animations
- **Lucide React**: Icon library
- **React Router**: Client-side routing

### Security
- **JWT Authentication**: Secure token-based auth
- **Email Verification**: OTP-based email verification
- **Rate Limiting**: API request throttling
- **CORS Protection**: Cross-origin request security
- **Input Validation**: Comprehensive data validation

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis (optional, for caching)
- SMTP server (Gmail, SendGrid, etc.)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/safenetai.git
cd safenetai
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Environment Configuration
```bash
# Copy example configuration
cp email_config_example.txt .env

# Edit .env with your settings
nano .env
```

Required environment variables:
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/safenetai

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Site Configuration
SITE_BASE_URL=http://localhost:3000
EMAIL_TOKEN_TTL_HOURS=24

# Logging Configuration
LOG_LEVEL_ROOT=WARNING
LOG_LEVEL_CONSOLE=INFO
LOG_LEVEL_AUTH=INFO
LOG_LEVEL_AI=INFO
LOG_LEVEL_RULES=INFO
LOG_LEVEL_TRANSACTIONS=INFO
LOG_LEVEL_SYSTEM=INFO
```

#### Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Generate fake data (optional)
python manage.py generate_fake_data --users 20 --transactions 100
```

#### Start Backend Server
```bash
python manage.py runserver 8000
```

### 3. Frontend Setup

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Environment Configuration
```bash
# Create .env file
cp .env.example .env

# Edit with your backend URL
VITE_API_URL=http://localhost:8000
```

#### Start Development Server
```bash
npm run dev
```

## 🧪 Testing with Fake Data

### 1. Generate Test Data
```bash
cd backend
python manage.py generate_fake_data --users 20 --transactions 100 --clear
```

This creates:
- 1 admin user (admin@safenetai.com / admin123)
- 20 regular users (password: password123)
- 100 transactions with various risk levels
- Fraud alerts and OTPs

### 2. Test User Flows

#### Client Testing
1. **Login as Client**:
   - Use any generated user: `john.smith1@example.com` / `password123`
   - Navigate to `/client-dashboard`

2. **Create Transactions**:
   - Go to `/transfer`
   - Try different amounts and transaction types
   - High amounts (>10,000 DZD) will trigger OTP verification

3. **OTP Verification**:
   - Check email for OTP code
   - Enter code in the verification modal
   - Complete the transaction

#### Admin Testing
1. **Login as Admin**:
   - Use: `admin@safenetai.com` / `admin123`
   - Navigate to `/admin-dashboard`

2. **Review Fraud Alerts**:
   - Go to `/admin/fraud-alerts`
   - Review and approve/reject transactions

3. **View System Logs**:
   - Go to `/admin/logs`
   - Browse different log categories

4. **Manage Rules**:
   - Go to `/admin/rules`
   - Adjust thresholds and rule settings

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/verify-otp/` - Email verification

### Transactions
- `GET /api/client/transactions/` - List user transactions
- `POST /api/client/transactions/` - Create transaction
- `POST /api/client/transactions/{id}/verify_otp/` - Verify OTP
- `POST /api/client/transactions/{id}/resend_otp/` - Resend OTP

### Admin
- `GET /api/admin/transactions/` - List all transactions
- `GET /api/admin/fraud-alerts/` - List fraud alerts
- `PATCH /api/admin/fraud-alerts/{id}/approve/` - Approve transaction
- `PATCH /api/admin/fraud-alerts/{id}/reject/` - Reject transaction

### System
- `GET /api/system/logs/` - View system logs
- `GET /api/system/logs/stats/` - Log statistics
- `GET /api/system/info/` - System information

## 🔧 Configuration

### Risk Engine Configuration
Edit thresholds in Django admin or via API:
- `large_amount`: Maximum transaction amount (default: 10,000 DZD)
- `high_frequency_count`: Max transactions per hour (default: 5)
- `low_balance_threshold`: Minimum balance after withdrawal (default: 1,000 DZD)

### Email Configuration
Configure SMTP settings in `.env`:
```bash
# Gmail Example
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Logging Configuration
Adjust log levels in `.env`:
```bash
LOG_LEVEL_AUTH=INFO      # Authentication logs
LOG_LEVEL_AI=INFO        # AI/ML prediction logs
LOG_LEVEL_RULES=INFO     # Rule engine logs
LOG_LEVEL_TRANSACTIONS=INFO  # Transaction logs
LOG_LEVEL_SYSTEM=INFO    # System logs
```

## 🚨 Security Features

### Transaction Security
- **Risk Scoring**: Every transaction gets a risk score (0-100)
- **OTP Verification**: High-risk transactions require email OTP
- **Fraud Alerts**: Suspicious transactions flagged for review
- **Balance Validation**: Prevents overdrafts

### User Security
- **Email Verification**: Required for account activation
- **JWT Tokens**: Secure authentication
- **Password Requirements**: Strong password enforcement
- **Session Management**: Secure session handling

### System Security
- **Input Validation**: Comprehensive data validation
- **SQL Injection Protection**: Django ORM protection
- **XSS Protection**: Content Security Policy
- **CSRF Protection**: Cross-site request forgery protection

## 📈 Monitoring & Logging

### Log Files
- `logs/auth.log` - Authentication events
- `logs/ai.log` - AI/ML predictions
- `logs/rules.log` - Rule engine evaluations
- `logs/transactions.log` - Transaction processing
- `logs/system.log` - General system events
- `logs/errors.log` - Error tracking

### Admin Monitoring
- **Real-time Dashboard**: System statistics and alerts
- **Log Viewer**: Web-based log browsing
- **System Health**: Database, cache, and email status
- **Performance Metrics**: Response times and throughput

## 🐛 Troubleshooting

### Common Issues

#### Email Not Sending
1. Check SMTP configuration in `.env`
2. Verify email credentials
3. Check firewall/network settings
4. Test with different SMTP provider

#### OTP Not Working
1. Check email delivery
2. Verify OTP expiration (10 minutes)
3. Check database for OTP records
4. Review email service logs

#### High Risk Scores
1. Review transaction amounts
2. Check user transaction history
3. Adjust risk thresholds
4. Review rule configurations

#### Database Issues
1. Check PostgreSQL connection
2. Verify database credentials
3. Run migrations: `python manage.py migrate`
4. Check database logs

### Debug Mode
Enable debug mode in `.env`:
```bash
DEBUG=True
```

### Log Analysis
View logs in real-time:
```bash
# Backend logs
tail -f logs/system.log

# Frontend logs
npm run dev
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

## 🔄 Updates

Stay updated with the latest features:
```bash
git pull origin main
pip install -r requirements.txt
python manage.py migrate
npm install
```

---

**SafeNetAi** - Protecting your transactions with AI-powered security.
