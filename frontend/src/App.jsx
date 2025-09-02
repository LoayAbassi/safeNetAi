import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import Login from './pages/Login';
import Register from './pages/Register';
import VerifyOTP from './pages/VerifyOTP';
import Dashboard from './pages/Dashboard';
import ClientDashboard from './pages/ClientDashboard';
import Transfer from './pages/Transfer';
import AdminDashboard from './pages/admin/Dashboard';
import Clients from './pages/admin/Clients';
import Transactions from './pages/admin/Transactions';
import FraudAlerts from './pages/admin/FraudAlerts';
import Rules from './pages/admin/Rules';
import Logs from './pages/admin/Logs';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import './styles/globals.css';

// Protected Route Component
const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && !user?.is_staff) {
    return <Navigate to="/client-dashboard" replace />;
  }

  return children;
};

// Role-based redirect component
const RoleBasedRedirect = () => {
  const { user } = useAuth();
  
  if (user?.is_staff) {
    return <Navigate to="/admin-dashboard" replace />;
  } else {
    return <Navigate to="/client-dashboard" replace />;
  }
};

// Layout Component with Navbar and Sidebar
const Layout = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  useEffect(() => {
    const handleToggleSidebar = () => {
      setIsSidebarOpen(false);
    };

    window.addEventListener('toggleSidebar', handleToggleSidebar);
    return () => window.removeEventListener('toggleSidebar', handleToggleSidebar);
  }, []);

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar isOpen={isSidebarOpen} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar toggleSidebar={toggleSidebar} isSidebarOpen={isSidebarOpen} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

// Main App Component
const AppContent = () => {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/verify-otp" element={<VerifyOTP />} />
        
        {/* Role-based redirect */}
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <RoleBasedRedirect />
            </ProtectedRoute>
          } 
        />
        
        {/* Client Routes */}
        <Route 
          path="/client-dashboard" 
          element={
            <ProtectedRoute>
              <Layout>
                <ClientDashboard />
              </Layout>
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/transfer" 
          element={
            <ProtectedRoute>
              <Layout>
                <Transfer />
              </Layout>
            </ProtectedRoute>
          } 
        />
        
        {/* Admin Routes */}
        <Route 
          path="/admin-dashboard" 
          element={
            <ProtectedRoute requireAdmin={true}>
              <Layout>
                <AdminDashboard />
              </Layout>
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin/clients" 
          element={
            <ProtectedRoute requireAdmin={true}>
              <Layout>
                <Clients />
              </Layout>
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin/transactions" 
          element={
            <ProtectedRoute requireAdmin={true}>
              <Layout>
                <Transactions />
              </Layout>
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin/fraud-alerts" 
          element={
            <ProtectedRoute requireAdmin={true}>
              <Layout>
                <FraudAlerts />
              </Layout>
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin/rules" 
          element={
            <ProtectedRoute requireAdmin={true}>
              <Layout>
                <Rules />
              </Layout>
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin/logs" 
          element={
            <ProtectedRoute requireAdmin={true}>
              <Layout>
                <Logs />
              </Layout>
            </ProtectedRoute>
          } 
        />
        
        {/* Default Route */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  );
};

// Root App Component with Auth Provider
const App = () => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;
