# SafeNetAI - AI-Powered Financial Fraud Detection

## 🎯 Overview

SafeNetAI secures financial transactions using AI/ML fraud detection, location-based verification, and real-time risk assessment with automated OTP verification for suspicious activities.

**Key Features:**
- 🤖 AI/ML fraud detection engine
- 📍 Location-based security (effective distance)
- 🔐 Email OTP for high-risk transactions  
- 👥 Client & Admin dashboards
- 📧 Automated email notifications
- 📊 Real-time risk scoring (0-100)

---

## 🚀 Quick Setup

### Prerequisites
- Python 3.8+, Node.js 16+
- Gmail account (for SMTP)

### 1. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

pip install -r requirements.txt
cp email_config_example.txt .env
# Edit .env: EMAIL_HOST_USER & EMAIL_HOST_PASSWORD

python manage.py migrate
python manage.py setup_initial_data
python manage.py runserver 8000
```

### 2. Frontend  
```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

### 3. Access
- **App**: http://localhost:5173
- **Admin**: http://localhost:8000/admin

---

## 💡 How to Use

### For Users
1. **Register** → Allow location access → Verify email
2. **Transfer Money** → Enter amount & recipient → Risk assessment 
3. **If High Risk** → Verify OTP from email → Complete transaction

### For Admins
1. **Monitor** real-time transactions and fraud alerts
2. **Manage** client accounts and system configuration
3. **Review** flagged transactions and adjust risk thresholds

---

## ⚙️ Configuration

### Email Setup (Gmail)
1. Enable 2FA on Gmail
2. Generate App Password (16 chars)
3. Update `.env`:
```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Risk Thresholds (Admin configurable)
- **Location**: 50km max distance
- **Large Amount**: 10,000 DZD threshold
- **OTP Trigger**: Risk score ≥ 70
- **Frequency**: 5 transactions/hour limit

---

## 🛡️ Security Features

### Location Intelligence
- Compares transaction location with home & last verified location
- Uses **effective distance** (shortest path) for decisions
- Updates last known location only after OTP success

### AI Risk Engine
- **Rule-Based**: Amount, frequency, time, location analysis
- **ML Model**: Pattern recognition with Isolation Forest
- **Real-Time**: Instant risk scoring (0-100 scale)
- **Adaptive**: Learns from verified transactions

### OTP Security
- Email-based 6-digit codes
- 10-minute expiration, 3-attempt limit
- Mandatory for distance violations

---

## 🏗️ Architecture

**Backend**: Django 4.2, PostgreSQL/SQLite, Scikit-learn  
**Frontend**: React 18, Vite, Tailwind CSS

```
safeNetAi/
├── backend/
│   ├── apps/
│   │   ├── risk/          # AI fraud detection
│   │   ├── transactions/  # Processing & OTP
│   │   ├── users/         # Authentication
│   │   └── system/        # Utilities
│   └── logs/              # Categorized logs
├── frontend/src/
│   ├── pages/             # Dashboards
│   └── components/        # UI components
└── README.md
```

---

## 🚀 Production

### Environment
```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:pass@host/db
EMAIL_HOST_USER=production@yourdomain.com
```

### Deploy
```bash
# Build frontend
cd frontend && npm run build

# Backend
cd backend
python manage.py migrate
python manage.py collectstatic
# Use Gunicorn + Nginx
```

---

## 🔧 Development

### Commands
```bash
# Database
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Frontend
npm run build    # Production build
npm run preview  # Preview build
```

### Adding Features
- **Backend**: Create apps in `backend/apps/`
- **Frontend**: Add components in `frontend/src/`
- **API**: Define endpoints in `urls.py`

---

## 🆘 Troubleshooting

**Email not working?**
- Check Gmail app password (16 chars, not regular password)
- Verify 2FA enabled on Gmail

**Location issues?**
- Enable browser location permissions
- Use HTTPS in production

**Database errors?**
- Run `python manage.py migrate`
- Check credentials in `.env`

**Import errors?**
- Activate virtual environment
- `pip install -r requirements.txt`

### Debug
- **Logs**: `backend/logs/` directory
- **Admin**: Django admin panel
- **Verify**: Run `python verify_system.py`

---

## 📊 API Endpoints

### Auth
- `POST /api/auth/register/` - Register user
- `POST /api/auth/login/` - Login
- `POST /api/auth/verify-otp/` - Verify email

### Transactions
- `GET /api/client/transactions/` - List transactions
- `POST /api/client/transactions/` - Create transaction
- `POST /api/client/transactions/{id}/verify_otp/` - Verify OTP

### Admin
- `GET /api/admin/dashboard/` - System stats
- `GET /api/admin/fraud-alerts/` - Review alerts
- `GET /api/admin/clients/` - Manage clients

---

**SafeNetAI** - Intelligent Financial Security 🛡️

*Built with Django + React • AI-Powered • Production Ready*

