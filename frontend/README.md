# SafeNetAi Frontend

A modern React application for the SafeNetAi fraud detection system, built with Vite, Tailwind CSS, and featuring real-time fraud detection interfaces.

## ✅ **Current System Status (January 2025)**

### **✓ Frontend Components Status:**
- **React 18**: Latest React version with concurrent features ✅
- **Vite Build**: Fast development server running on port 5173 ✅
- **Authentication Flow**: Login, registration, and OTP verification working ✅
- **Role-based Routing**: Separate client and admin interfaces ✅
- **API Integration**: Seamless connection to Django backend ✅
- **Responsive Design**: Mobile-friendly UI across all devices ✅
- **Real-time Updates**: Live transaction status and fraud alerts ✅

## 🚀 **Features**

### **Core User Interface**
- **Modern React 18**: Hooks, concurrent features, and suspense
- **Vite Build Tool**: Lightning-fast development and build process
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **Framer Motion**: Smooth animations and transitions
- **Lucide React**: Beautiful, consistent icon library

### **Authentication & Security**
- **JWT Token Management**: Automatic token handling and refresh
- **Email OTP Verification**: Complete OTP flow with countdown timers
- **Role-based Access**: Automatic routing based on user permissions
- **Secure Storage**: Safe token storage and session management

### **Client Interface**
- **Dashboard**: Profile overview, balance display, recent transactions
- **Transaction Creation**: Transfer form with real-time validation
- **Transaction History**: Complete transaction list with risk scores
- **Fraud Alerts**: User-specific security notifications
- **OTP Verification**: Modal-based OTP input with resend functionality

### **Admin Interface**
- **Admin Dashboard**: System statistics and fraud monitoring
- **Client Management**: View and manage all user accounts
- **Transaction Monitoring**: Real-time transaction oversight
- **Fraud Alert Management**: Review, approve, and reject suspicious transactions
- **System Logs**: Web-based log viewer with filtering
- **Rule Configuration**: Fraud detection threshold management

## 🛠️ **Technology Stack**

- **React 18.2.0** - Modern UI framework with concurrent features
- **Vite 5.0.8** - Next-generation build tool for faster development
- **Tailwind CSS 3.4.0** - Utility-first CSS framework
- **Framer Motion 10.16.16** - Production-ready motion library
- **Lucide React 0.303.0** - Beautiful & consistent icon library
- **Axios 1.6.2** - Promise-based HTTP client
- **React Router DOM 6.20.1** - Client-side routing
- **TypeScript Support** - Optional type safety

## 📋 **Prerequisites**

- **Node.js 16+** (18+ recommended)
- **npm 8+** or **yarn 1.22+**
- **Windows PowerShell** (for Windows users) or Terminal (macOS/Linux)
- **Backend API** running on http://localhost:8000

## 🚀 **Quick Start**

### 1. Install Dependencies
```powershell
cd frontend
npm install
```

### 2. Environment Configuration
```powershell
# Create .env file
New-Item -Path ".env" -ItemType File
```

Add to `.env`:
```env
# Backend API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Optional: Development settings
VITE_NODE_ENV=development
```

### 3. Start Development Server
```powershell
npm run dev
```

✅ **Frontend will be available at**: http://localhost:5173
✅ **Hot reload enabled**: Changes update instantly
✅ **Backend required**: Make sure Django server is running on port 8000

### 4. Build for Production
```powershell
# Create optimized production build
npm run build

# Preview production build locally
npm run preview
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ErrorMessage.tsx
│   │   └── LoadingSpinner.tsx
│   ├── pages/              # Page components
│   │   ├── admin/          # Admin pages
│   │   │   └── AdminRisk.jsx
│   │   ├── index.tsx       # Dashboard
│   │   ├── Login.jsx       # Login page
│   │   └── Transfer.jsx    # Transfer creation
│   ├── styles/             # Global styles
│   │   └── globals.css
│   ├── api.js              # API configuration
│   ├── App.jsx             # Main app component
│   └── main.jsx            # Entry point
├── index.html              # HTML template
├── package.json            # Dependencies
├── vite.config.js          # Vite configuration
└── README.md               # This file
```

## 🔧 **Configuration**

### **Environment Variables**

Create a `.env` file with:

```env
# Required: Backend API URL
VITE_API_BASE_URL=http://localhost:8000

# Optional: Development settings
VITE_NODE_ENV=development
VITE_DEBUG_MODE=true

# Optional: Analytics (for production)
VITE_ANALYTICS_ID=your-analytics-id
```

### **API Configuration**

The application uses Axios for API communication (`src/utils/api.js`):

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for JWT authentication
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle token refresh or redirect to login
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        // Attempt token refresh
        try {
          const response = await axios.post('/api/auth/refresh/', {
            refresh: refreshToken
          });
          localStorage.setItem('access_token', response.data.access);
          return api.request(error.config);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.clear();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

## 📖 Usage Guide

### Authentication Flow

1. **Login**: Users can log in with email and password
2. **Registration**: New users register with profile matching credentials
3. **OTP Verification**: Email verification with one-time password
4. **Token Management**: Automatic JWT token handling

### Client Features

- **Dashboard**: View profile, balance, and recent transactions
- **Transaction History**: Complete transaction history with status
- **Transfer Creation**: Create new transfers with location tracking
- **Fraud Alerts**: View and manage fraud alerts

### Admin Features

- **Client Management**: View and manage all client profiles
- **Transaction Monitoring**: Monitor all system transactions
- **Fraud Alert Management**: Review and approve/reject fraud alerts
- **Risk Configuration**: Configure fraud detection thresholds

## 🧪 **Testing**

### **Run Tests**
```powershell
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

### **Testing User Flows**

#### **Authentication Testing**
1. **Registration Flow**: Test email validation, OTP delivery, verification
2. **Login Flow**: Test JWT token handling, role detection, routing
3. **OTP Verification**: Test countdown timer, resend functionality, error handling

#### **Transaction Testing**
1. **Transaction Creation**: Test form validation, API integration, success/error states
2. **High-Risk Transactions**: Test OTP modal, verification flow, completion
3. **Real-time Updates**: Test balance updates, transaction status changes

## 🏗️ Build

### Development Build
```bash
npm run dev
```

### Production Build
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## 🔒 Security Features

- **JWT Token Management**: Secure token storage and refresh
- **Input Validation**: Client-side form validation
- **CORS Handling**: Proper cross-origin request handling
- **Error Handling**: Comprehensive error management

## 🎨 UI Components

### Material-UI Integration

The application uses Material-UI v5 with the following key components:

- **Theme**: Custom theme with SafeNetAi branding
- **Components**: Buttons, forms, tables, cards, and more
- **Responsive Design**: Mobile-first approach
- **Dark/Light Mode**: Theme switching capability

### Key Components

- **LoadingSpinner**: Reusable loading indicator
- **ErrorMessage**: Standardized error display
- **DataTable**: Reusable table component
- **FormDialog**: Modal form dialogs

## 📱 Responsive Design

The application is fully responsive and works on:

- **Desktop**: Full-featured interface
- **Tablet**: Optimized layout
- **Mobile**: Touch-friendly interface

## 🚀 Performance

- **Code Splitting**: Automatic route-based code splitting
- **Lazy Loading**: Components loaded on demand
- **Optimized Builds**: Vite for fast development and optimized production builds
- **Caching**: Efficient caching strategies

## 🔧 Development

### Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build

# Testing
npm test             # Run tests
npm run test:coverage # Run tests with coverage

# Linting
npm run lint         # Run ESLint
npm run lint:fix     # Fix linting issues
```

### Code Style

The project uses:
- **ESLint** for code linting
- **Prettier** for code formatting
- **TypeScript** for type safety

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check `VITE_API_BASE_URL` in `.env.local`
   - Ensure backend server is running
   - Check CORS configuration

2. **Authentication Issues**
   - Clear localStorage and try again
   - Check token expiration
   - Verify email verification status

3. **Build Errors**
   - Clear node_modules and reinstall
   - Check for TypeScript errors
   - Verify all dependencies are installed

## 🤝 Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Test on multiple devices

## 📝 License

This project is licensed under the MIT License.
