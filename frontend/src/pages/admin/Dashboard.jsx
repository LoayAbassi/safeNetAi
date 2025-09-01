import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  CreditCard, 
  AlertTriangle, 
  TrendingUp, 
  DollarSign,
  Shield,
  Activity,
  BarChart3
} from 'lucide-react';
import api from '../../api';

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    totalClients: 0,
    totalTransactions: 0,
    pendingFraudAlerts: 0,
    totalBalance: 0,
    recentTransactions: [],
    fraudAlerts: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch statistics
      const [clientsRes, transactionsRes, fraudAlertsRes] = await Promise.all([
        api.get('/api/admin/clients/'),
        api.get('/api/admin/transactions/'),
        api.get('/api/admin/fraud-alerts/')
      ]);

      const totalBalance = clientsRes.data.results?.reduce((sum, client) => 
        sum + parseFloat(client.balance), 0) || 0;

      const pendingAlerts = fraudAlertsRes.data.results?.filter(alert => 
        alert.status === 'Pending') || [];

      setStats({
        totalClients: clientsRes.data.count || 0,
        totalTransactions: transactionsRes.data.count || 0,
        pendingFraudAlerts: pendingAlerts.length,
        totalBalance: totalBalance,
        recentTransactions: transactionsRes.data.results?.slice(0, 5) || [],
        fraudAlerts: fraudAlertsRes.data.results?.slice(0, 5) || []
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('ar-DZ', {
      style: 'currency',
      currency: 'DZD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ar-DZ', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getRiskLevelColor = (level) => {
    switch (level) {
      case 'High': return 'text-red-600 bg-red-100';
      case 'Medium': return 'text-yellow-600 bg-yellow-100';
      case 'Low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const statCards = [
    {
      title: 'Total Clients',
      value: stats.totalClients,
      icon: Users,
      color: 'bg-blue-500',
      change: '+12%'
    },
    {
      title: 'Total Transactions',
      value: stats.totalTransactions,
      icon: CreditCard,
      color: 'bg-green-500',
      change: '+8%'
    },
    {
      title: 'Pending Alerts',
      value: stats.pendingFraudAlerts,
      icon: AlertTriangle,
      color: 'bg-red-500',
      change: '-5%'
    },
    {
      title: 'Total Balance',
      value: formatCurrency(stats.totalBalance),
      icon: DollarSign,
      color: 'bg-purple-500',
      change: '+15%'
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome to the SafeNetAi administration panel</p>
      </motion.div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-white rounded-lg shadow-md p-6 border border-gray-200"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                  <p className="text-xs text-green-600 mt-1">{stat.change} from last month</p>
                </div>
                <div className={`p-3 rounded-full ${stat.color}`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Transactions */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="bg-white rounded-lg shadow-md border border-gray-200"
        >
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Recent Transactions</h2>
              <TrendingUp className="h-5 w-5 text-gray-400" />
            </div>
          </div>
          <div className="p-6">
            {stats.recentTransactions.length > 0 ? (
              <div className="space-y-4">
                {stats.recentTransactions.map((transaction) => (
                  <div key={transaction.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">
                        {transaction.client?.first_name} {transaction.client?.last_name}
                      </p>
                      <p className="text-sm text-gray-600">
                        {transaction.transaction_type} • {formatDate(transaction.created_at)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900">
                        {formatCurrency(transaction.amount)}
                      </p>
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                        transaction.status === 'completed' ? 'bg-green-100 text-green-800' :
                        transaction.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {transaction.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">No recent transactions</p>
            )}
          </div>
        </motion.div>

        {/* Fraud Alerts */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="bg-white rounded-lg shadow-md border border-gray-200"
        >
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Fraud Alerts</h2>
              <AlertTriangle className="h-5 w-5 text-red-500" />
            </div>
          </div>
          <div className="p-6">
            {stats.fraudAlerts.length > 0 ? (
              <div className="space-y-4">
                {stats.fraudAlerts.map((alert) => (
                  <div key={alert.id} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-medium text-gray-900">
                        Transaction #{alert.transaction?.id}
                      </p>
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getRiskLevelColor(alert.level)}`}>
                        {alert.level} Risk
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      {alert.message}
                    </p>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>Score: {alert.risk_score}</span>
                      <span>{formatDate(alert.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">No fraud alerts</p>
            )}
          </div>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="bg-white rounded-lg shadow-md border border-gray-200 p-6"
      >
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center justify-center space-x-2 p-4 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors duration-200">
            <Users className="h-5 w-5 text-blue-600" />
            <span className="font-medium text-blue-900">Manage Clients</span>
          </button>
          <button className="flex items-center justify-center space-x-2 p-4 bg-green-50 hover:bg-green-100 rounded-lg transition-colors duration-200">
            <CreditCard className="h-5 w-5 text-green-600" />
            <span className="font-medium text-green-900">View Transactions</span>
          </button>
          <button className="flex items-center justify-center space-x-2 p-4 bg-red-50 hover:bg-red-100 rounded-lg transition-colors duration-200">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <span className="font-medium text-red-900">Review Alerts</span>
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default AdminDashboard;
