import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  LogOut, 
  User, 
  DollarSign, 
  CreditCard, 
  TrendingUp, 
  AlertTriangle,
  RefreshCw,
  Plus
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import api from '../api';
import { useTranslation } from 'react-i18next';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const { t, i18n } = useTranslation();

  const formatCurrency = (amount) => {
    const locale = i18n.language === 'ar' ? 'ar-DZ' : 
                  i18n.language === 'fr' ? 'fr-FR' : 'en-US';
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: 'DZD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [profileRes, transactionsRes] = await Promise.all([
        api.get('/api/client/profile/me/'),
        api.get('/api/client/transactions/')
      ]);
      
      setProfile(profileRes.data);
      setTransactions(transactionsRes.data.slice(0, 5)); // Get last 5 transactions
    } catch (error) {
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">SafeNetAi Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/transfer')}
                className="btn-primary flex items-center"
              >
                <Plus className="h-4 w-4 mr-2" />
                Transfer
              </motion.button>
              {user?.is_staff && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => navigate('/admin/clients')}
                  className="btn-secondary flex items-center"
                >
                  <User className="h-4 w-4 mr-2" />
                  Admin
                </motion.button>
              )}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleLogout}
                className="btn-danger flex items-center"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </motion.button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-danger-50 border border-danger-200 rounded-lg flex items-center"
          >
            <AlertTriangle className="h-5 w-5 text-danger-500 mr-2" />
            <span className="text-danger-700">{error}</span>
          </motion.div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Card */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="card"
          >
            <div className="card-header">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <User className="h-5 w-5 mr-2" />
                Profile
              </h2>
            </div>
            {profile && (
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Name</label>
                  <p className="text-gray-900">{profile.full_name}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Email</label>
                  <p className="text-gray-900">{user?.email}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Account Number</label>
                  <p className="text-gray-900 font-mono">{profile.bank_account_number}</p>
                </div>
                <div className="pt-4 border-t border-gray-200">
                  <label className="text-sm font-medium text-gray-500">Balance</label>
                  <p className="text-2xl font-bold text-primary-600">
                    {formatCurrency(profile.balance)}
                  </p>
                </div>

              </div>
            )}
          </motion.div>

          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card"
          >
            <div className="card-header">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <TrendingUp className="h-5 w-5 mr-2" />
                Quick Actions
              </h2>
            </div>
            <div className="space-y-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => navigate('/transfer')}
                className="btn-primary w-full flex items-center justify-center py-3"
              >
                <Plus className="h-5 w-5 mr-2" />
                New Transfer
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={fetchData}
                className="btn-secondary w-full flex items-center justify-center py-3"
              >
                <RefreshCw className="h-5 w-5 mr-2" />
                Refresh Data
              </motion.button>
            </div>
          </motion.div>

          {/* Recent Transactions */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="card lg:col-span-3"
          >
            <div className="card-header">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <CreditCard className="h-5 w-5 mr-2" />
                Recent Transactions
              </h2>
            </div>
            {transactions.length > 0 ? (
              <div className="overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="table-header">Type</th>
                      <th className="table-header">Amount</th>
                      <th className="table-header">Status</th>
                      <th className="table-header">Date</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {transactions.map((transaction, index) => (
                      <motion.tr
                        key={transaction.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 * index }}
                        className="hover:bg-gray-50"
                      >
                        <td className="table-cell">
                          <span className="capitalize">{transaction.transaction_type}</span>
                        </td>
                        <td className="table-cell font-medium">
                          {formatCurrency(transaction.amount)}

                        </td>
                        <td className="table-cell">
                          <span className={`badge ${
                            transaction.status === 'completed' ? 'badge-success' :
                            transaction.status === 'pending' ? 'badge-warning' : 'badge-danger'
                          }`}>
                            {transaction.status}
                          </span>
                        </td>
                        <td className="table-cell text-gray-500">
                          {new Date(transaction.created_at).toLocaleDateString()}
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8">
                <DollarSign className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No transactions yet.</p>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
