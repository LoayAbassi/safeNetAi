import React from 'react';
import { motion } from 'framer-motion';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Users, 
  CreditCard, 
  AlertTriangle, 
  Settings, 
  TrendingUp,
  Shield,
  BarChart3,
  FileText
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const Sidebar = ({ isOpen }) => {
  const { user, isAuthenticated } = useAuth();
  const location = useLocation();

  const isAdmin = user?.is_staff;

  const clientNavItems = [
    { name: 'Dashboard', icon: Home, path: '/client-dashboard' },
    { name: 'Transfer', icon: CreditCard, path: '/transfer' },
    { name: 'Transactions', icon: TrendingUp, path: '/transactions' },
    { name: 'Fraud Alerts', icon: AlertTriangle, path: '/fraud-alerts' },
  ];

  const adminNavItems = [
    { name: 'Dashboard', icon: Home, path: '/admin-dashboard' },
    { name: 'Clients', icon: Users, path: '/admin/clients' },
    { name: 'Transactions', icon: CreditCard, path: '/admin/transactions' },
    { name: 'Fraud Alerts', icon: AlertTriangle, path: '/admin/fraud-alerts' },
    { name: 'Rules & Thresholds', icon: Settings, path: '/admin/rules' },
    { name: 'Analytics', icon: BarChart3, path: '/admin/analytics' },
    { name: 'System Logs', icon: FileText, path: '/admin/logs' },
  ];

  const navItems = isAdmin ? adminNavItems : clientNavItems;

  const sidebarVariants = {
    open: {
      x: 0,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 30
      }
    },
    closed: {
      x: "-100%",
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 30
      }
    }
  };

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <motion.div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => window.dispatchEvent(new CustomEvent('toggleSidebar'))}
        />
      )}

      {/* Sidebar */}
      <motion.aside
        className={`fixed top-0 left-0 z-50 h-full w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        variants={sidebarVariants}
        initial="closed"
        animate={isOpen ? "open" : "closed"}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-center h-16 px-4 border-b border-gray-200">
            <motion.div 
              className="flex items-center space-x-2"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Shield className="h-8 w-8 text-primary-600" />
              <span className="text-lg font-bold text-gray-900">SafeNetAi</span>
            </motion.div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navItems.map((item, index) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <motion.div
                  key={item.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 * index }}
                >
                  <Link
                    to={item.path}
                    className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      isActive
                        ? 'bg-primary-100 text-primary-700 border-r-2 border-primary-500'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`}
                  >
                    <Icon className={`h-5 w-5 ${isActive ? 'text-primary-600' : 'text-gray-400'}`} />
                    <span>{item.name}</span>
                  </Link>
                </motion.div>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            <motion.div 
              className="text-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <p className="text-xs text-gray-500">
                {isAdmin ? 'Administrator Panel' : 'Client Portal'}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                SafeNetAi v1.0
              </p>
            </motion.div>
          </div>
        </div>
      </motion.aside>
    </>
  );
};

export default Sidebar;
