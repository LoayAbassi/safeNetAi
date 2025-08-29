# SafeNetAi Backend - Banking Fraud Detection System

A comprehensive Django REST Framework backend for a banking fraud detection system that combines admin-driven client management, custom fraud detection rules, and AI-assisted decision-making.

## 🚀 Features

### Authentication & User Management
- **JWT-based authentication** with access and refresh tokens
- **Role-based access control** (Admin/Client)
- **Restricted registration** - users can only register if they have an existing client profile
- **Client profile management** with unique National ID and Bank Account Number

### Fraud Detection Engine
- **Configurable rules and thresholds** for fraud detection
- **Real-time transaction monitoring** with automatic fraud alerts
- **Risk scoring system** based on multiple factors:
  - Large withdrawal amounts
  - High transaction frequency
  - Low balance after transactions
  - Statistical outliers (z-score analysis)

### Admin Panel
- **Client profile management** (CRUD operations)
- **Transaction monitoring** across all clients
- **Fraud alert management** with status updates
- **Rule and threshold configuration**
- **Search and filtering** capabilities

### API Endpoints

#### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration (requires existing profile)

#### Client Endpoints
- `GET /api/client/profile/` - Get client profile
- `GET /api/client/profile/me/` - Get current user's profile
- `GET /api/client/transactions/` - List user's transactions
- `POST /api/client/transactions/` - Create new transaction
- `GET /api/client/fraud-alerts/` - List user's fraud alerts

#### Admin Endpoints
- `GET /api/admin/clients/` - List all clients
- `POST /api/admin/clients/` - Create new client
- `GET /api/admin/clients/search/?q=<query>` - Search clients
- `GET /api/admin/transactions/` - List all transactions
- `GET /api/admin/transactions/search/?q=<query>` - Search transactions
- `GET /api/admin/fraud-alerts/` - List all fraud alerts
- `PATCH /api/admin/fraud-alerts/{id}/update_status/` - Update alert status
- `GET /api/admin/thresholds/` - List fraud detection thresholds
- `POST /api/admin/thresholds/` - Create/update thresholds
- `GET /api/admin/rules/` - List fraud detection rules
- `POST /api/admin/rules/` - Create/update rules

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd safeNetAi/backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Set up initial data**
   ```bash
   python manage.py setup_initial_data
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The server will be available at `http://localhost:8000`

## 🔐 Default Credentials

After running the setup command, you'll have:

### Admin User
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@safenetai.com`

### Sample Client Profiles
- **John Doe** (National ID: 123456789)
- **Jane Smith** (National ID: 987654321)
- **Bob Johnson** (National ID: 456789123)

## 📊 Fraud Detection Rules

The system includes several configurable fraud detection rules:

### 1. Large Withdrawal Rule
- **Threshold**: $10,000 (configurable)
- **Risk Score**: +30 points
- **Trigger**: Withdrawal amount exceeds threshold

### 2. High Frequency Rule
- **Threshold**: 5 transactions per hour (configurable)
- **Risk Score**: +25 points
- **Trigger**: Multiple transactions in short time period

### 3. Low Balance Rule
- **Threshold**: $100 minimum balance (configurable)
- **Risk Score**: +20 points
- **Trigger**: Transaction leaves balance below threshold

### 4. Statistical Outlier Rule
- **Threshold**: 2.5 standard deviations (configurable)
- **Risk Score**: +15 points
- **Trigger**: Transaction amount is statistically unusual

## 🔧 Configuration

### Thresholds
Key thresholds can be configured via the admin panel or API:

- `LARGE_WITHDRAWAL_AMOUNT`: Maximum withdrawal amount before flagging
- `MAX_TRANSACTIONS_PER_HOUR`: Maximum transactions per hour
- `LOW_BALANCE_THRESHOLD`: Minimum balance after withdrawal
- `AVERAGE_TRANSACTION_AMOUNT`: Average transaction amount for statistical analysis
- `TRANSACTION_STD_DEV`: Standard deviation for transaction amounts

### Risk Levels
- **Low Risk**: 0-39 points
- **Medium Risk**: 40-69 points
- **High Risk**: 70+ points

## 🧪 Testing the API

### 1. Login as Admin
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. Create a Client Profile
```bash
curl -X POST http://localhost:8000/api/admin/clients/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "national_id": "111222333",
    "bank_account_number": "11111111",
    "balance": 5000.00
  }'
```

### 3. Register a User (requires existing profile)
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "email": "test@example.com",
    "national_id": "111222333"
  }'
```

### 4. Create a Transaction
```bash
curl -X POST http://localhost:8000/api/client/transactions/ \
  -H "Authorization: Bearer <client_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 15000.00,
    "transaction_type": "withdraw"
  }'
```

## 📁 Project Structure

```
backend/
├── apps/
│   ├── users/                 # User and client profile management
│   │   ├── models.py         # User and ClientProfile models
│   │   ├── serializers.py    # User serializers
│   │   ├── views.py          # User views
│   │   └── admin.py          # Admin interface
│   ├── transactions/         # Transaction and fraud alert management
│   │   ├── models.py         # Transaction and FraudAlert models
│   │   ├── serializers.py    # Transaction serializers
│   │   ├── views.py          # Transaction views
│   │   ├── signals.py        # Fraud detection signals
│   │   └── admin.py          # Admin interface
│   └── risk/                 # Fraud detection engine
│       ├── models.py         # Rule and Threshold models
│       ├── engine.py         # Fraud detection logic
│       ├── serializers.py    # Risk serializers
│       ├── admin_views.py    # Admin views
│       └── admin.py          # Admin interface
├── backend/
│   ├── settings.py           # Django settings
│   └── urls.py               # URL configuration
├── manage.py                 # Django management script
└── requirements.txt          # Python dependencies
```

## 🔒 Security Features

- **JWT Authentication** with configurable token lifetimes
- **Role-based permissions** ensuring users can only access their own data
- **CORS configuration** for frontend integration
- **Input validation** and sanitization
- **Unique constraints** on National ID and Bank Account Number

## 🚀 Deployment

For production deployment:

1. **Set environment variables**:
   ```bash
   export DJANGO_SECRET_KEY="your-secret-key"
   export DEBUG=False
   ```

2. **Use a production database** (PostgreSQL recommended)

3. **Configure static files** and media storage

4. **Set up proper logging** and monitoring

5. **Use HTTPS** for all communications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions, please contact the development team or create an issue in the repository.
