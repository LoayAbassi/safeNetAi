# SafeNetAi Frontend

A modern React application for the SafeNetAi fraud detection system, built with Material-UI and Vite.

## 🚀 Features

- **Modern UI/UX**: Material-UI components with responsive design
- **Authentication Flow**: Complete login, registration, and OTP verification
- **Client Dashboard**: Profile management and transaction history
- **Transaction Creation**: Transfer creation with geolocation capture
- **Admin Interface**: Complete admin panel for system management
- **Real-time Updates**: Live fraud detection and alert management
- **Mobile Responsive**: Works seamlessly on all devices

## 🛠️ Technology Stack

- **React 18** - UI framework
- **Material-UI (MUI)** - Component library
- **React Router** - Navigation
- **Axios** - HTTP client
- **Vite** - Build tool
- **TypeScript** - Type safety

## 📋 Prerequisites

- Node.js 16+
- npm or yarn

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Environment Configuration
Create a `.env.local` file in the frontend directory:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Start Development Server
```bash
npm run dev
```

The application will be available at http://localhost:3000

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

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file with the following variables:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Optional: Analytics
VITE_ANALYTICS_ID=your-analytics-id
```

### API Configuration

The application uses Axios for API communication. Configuration is in `src/api.js`:

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

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

## 🧪 Testing

### Run Tests
```bash
npm test
```

### Run Tests with Coverage
```bash
npm run test:coverage
```

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
