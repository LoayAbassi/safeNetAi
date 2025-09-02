# SafeNetAI - Complete Setup Guide (Windows PowerShell)

## 🎯 **Overview**

This guide provides step-by-step instructions for setting up SafeNetAI fraud detection system on Windows using PowerShell. Follow these instructions to get a fully functional system running locally.

## 📋 **Prerequisites**

### **Required Software**
- **Python 3.8+** (3.9+ recommended) - [Download from python.org](https://www.python.org/downloads/)
- **Node.js 16+** (18+ recommended) - [Download from nodejs.org](https://nodejs.org/)
- **Git** - [Download from git-scm.com](https://git-scm.com/)
- **Windows PowerShell 5.0+** (Built into Windows 10/11)

### **Required Accounts**
- **Gmail Account** with 2-factor authentication enabled
- **GitHub Account** (if cloning from repository)

### **Hardware Requirements**
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Internet**: Stable connection for package downloads

## 🚀 **Step-by-Step Setup**

### **Step 1: Clone Repository**

```powershell
# Open PowerShell as Administrator (recommended)
# Navigate to desired directory
cd C:\Users\$env:USERNAME\Desktop\projects

# Clone the repository
git clone https://github.com/yourusername/safeNetAi.git
cd safeNetAi
```

### **Step 2: Backend Setup**

#### **2.1 Create Virtual Environment**

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try activation again
venv\Scripts\Activate.ps1
```

**✅ Verification**: Your PowerShell prompt should show `(venv)` prefix

#### **2.2 Install Python Dependencies**

```powershell
# Ensure you're in the backend directory with venv activated
pip install --upgrade pip
pip install -r requirements.txt
```

**✅ Verification**: All packages should install without errors

#### **2.3 Environment Configuration**

```powershell
# Create .env file
New-Item -Path ".env" -ItemType File -Force
```

**Add the following content to `.env` file** (use notepad or your preferred editor):

```env
# Django Configuration
DEBUG=1
SECRET_KEY=xaUlkckAQwIcC1V3W28duX4cFd1elWsQ

# Database Configuration (SQLite for development)
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration (Gmail SMTP)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password

# Site Configuration
SITE_BASE_URL=http://localhost:5173
EMAIL_TOKEN_TTL_HOURS=24
```

#### **2.4 Gmail Setup for Email Service**

1. **Enable 2-Factor Authentication**:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification if not already enabled

2. **Generate App Password**:
   - In Security settings, click "App passwords"
   - Select "Mail" and "Other (custom name)"
   - Enter "SafeNetAI" as the name
   - **Copy the 16-character password** (this is your `EMAIL_HOST_PASSWORD`)

3. **Update .env file**:
   ```env
   EMAIL_HOST_USER=your-actual-email@gmail.com
   EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop  # Your 16-char App Password
   ```

#### **2.5 Database Setup**

```powershell
# Apply database migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
# Enter: email, first name, last name, password

# Set up initial data (thresholds and rules)
python manage.py setup_initial_data

# Generate test data (optional but recommended)
python manage.py generate_fake_data --users 10 --transactions 50
```

#### **2.6 Test Email Configuration**

```powershell
# Test email setup
python test_email_config.py
```

**Expected Output**: ✅ All email settings validated, SMTP connection successful

#### **2.7 Start Backend Server**

```powershell
# Start Django development server
python manage.py runserver 8000
```

**✅ Verification**: 
- Server starts without errors
- Visit http://localhost:8000/admin/ (should load Django admin)
- API accessible at http://localhost:8000/api/

### **Step 3: Frontend Setup**

**Open a new PowerShell window** (keep backend running in the first one)

#### **3.1 Navigate to Frontend Directory**

```powershell
cd C:\Users\$env:USERNAME\Desktop\projects\safeNetAi\frontend
```

#### **3.2 Install Node Dependencies**

```powershell
# Install all npm packages
npm install
```

**✅ Verification**: All packages should install without peer dependency warnings

#### **3.3 Frontend Environment Configuration**

```powershell
# Create .env file
New-Item -Path ".env" -ItemType File -Force
```

**Add to `.env` file**:
```env
# Backend API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Optional: Development settings
VITE_NODE_ENV=development
```

#### **3.4 Start Frontend Server**

```powershell
# Start Vite development server
npm run dev
```

**✅ Verification**:
- Server starts on http://localhost:5173
- Hot reload enabled
- Browser automatically opens (or manually visit http://localhost:5173)

## 🧪 **System Verification**

### **Test Backend API**

```powershell
# Test API health (in a new PowerShell window)
curl http://localhost:8000/api/auth/login/ -Method POST -ContentType "application/json" -Body '{"email":"test","password":"test"}'
```

**Expected**: Should return error response (not 500 error)

### **Test Frontend Connection**

1. **Open Browser**: http://localhost:5173
2. **Verify**: Login page loads with SafeNetAI branding
3. **Test Login**: Use superuser credentials created earlier

### **Test Complete User Flow**

1. **Admin Login**: 
   - Email: (your superuser email)
   - Password: (your superuser password)
   - Should redirect to `/admin-dashboard`

2. **Create Test Transaction**:
   - Navigate to transaction creation
   - Enter amount > 10,000 DZD (should trigger OTP)
   - Check email for OTP delivery

3. **Verify Fraud Detection**:
   - High amounts should show risk scores
   - OTP required for risky transactions
   - Admin can view fraud alerts

## 🔧 **Troubleshooting**

### **Common PowerShell Issues**

#### **Execution Policy Error**
```powershell
# Problem: Cannot run venv\Scripts\Activate.ps1
# Solution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### **Python Not Found**
```powershell
# Problem: 'python' is not recognized
# Solution: Add Python to PATH or use:
py -3.9 -m venv venv  # Use specific Python version
```

#### **Port Already in Use**
```powershell
# Problem: Port 8000 or 5173 already in use
# Solution: Kill process using port
netstat -ano | findstr :8000
taskkill /F /PID <PID_NUMBER>
```

### **Backend Issues**

#### **Database Errors**
```powershell
# Reset database (development only)
Remove-Item db.sqlite3 -Force
python manage.py migrate
python manage.py createsuperuser
```

#### **Email Not Sending**
1. ✅ Verify Gmail App Password is correct (16 characters)
2. ✅ Check 2-factor authentication is enabled
3. ✅ Test with `python test_email_config.py`
4. ✅ Check Windows Firewall/antivirus blocking SMTP

#### **AI Model Issues**
```powershell
# Verify model file exists
Get-ChildItem models\fraud_isolation.joblib
# Should show 1.77MB file

# Retrain if needed
python manage.py train_fraud_model
```

### **Frontend Issues**

#### **Node Modules Issues**
```powershell
# Clear cache and reinstall
Remove-Item node_modules -Recurse -Force
Remove-Item package-lock.json -Force
npm install
```

#### **Build Errors**
```powershell
# Clear Vite cache
npx vite --force
```

## 📊 **System Health Check**

After complete setup, verify all components:

### **Backend Health** ✅
- [ ] Django server running on port 8000
- [ ] Admin interface accessible
- [ ] API endpoints responding
- [ ] Database migrations applied
- [ ] Email configuration working
- [ ] AI model loaded (1.77MB file)

### **Frontend Health** ✅
- [ ] React server running on port 5173
- [ ] Login page loads correctly
- [ ] API communication working
- [ ] Authentication flow functional
- [ ] Role-based routing working

### **Integration Health** ✅
- [ ] User can register and verify email
- [ ] Transactions create successfully
- [ ] Risk engine evaluates transactions
- [ ] OTP emails deliver for high-risk transactions
- [ ] Admin can manage fraud alerts
- [ ] Logs are being generated in logs/ directory

## 🎉 **Next Steps**

Once setup is complete:

1. **Explore Admin Interface**: http://localhost:8000/admin/
2. **Test User Registration**: Create a new user account
3. **Create Test Transactions**: Test the fraud detection system
4. **Review System Logs**: Check logs/ directory for system activity
5. **Customize Settings**: Adjust fraud detection thresholds as needed

## 📞 **Support**

If you encounter issues:

1. **Check Logs**: Review logs/ directory for error details
2. **Verify Prerequisites**: Ensure all required software is installed
3. **Test Individual Components**: Backend, frontend, and database separately
4. **Review Documentation**: Check component-specific README files

---

**🎯 Congratulations! SafeNetAI is now fully operational on your Windows system.**