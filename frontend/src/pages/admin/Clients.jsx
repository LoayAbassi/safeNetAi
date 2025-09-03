import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Users, 
  Plus, 
  Search, 
  ArrowLeft,
  Eye,
  Edit,
  Trash2,
  AlertCircle,
  CheckCircle,
  X
} from 'lucide-react';
import api from '../../api';

const Clients = () => {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [newClient, setNewClient] = useState({
    first_name: '',
    last_name: '',
    national_id: '',
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      const response = await api.get('/api/admin/clients/');
      setClients(response.data);
    } catch (error) {
      setError('Failed to load clients');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateClient = async () => {
    try {
      await api.post('/api/admin/clients/', newClient);
      setOpenDialog(false);
      setNewClient({ first_name: '', last_name: '', national_id: '' });
      fetchClients();
    } catch (error) {
      setError('Failed to create client');
    }
  };

  const filteredClients = clients.filter(client =>
    client.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    client.last_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    client.national_id?.includes(searchTerm) ||
    client.bank_account_number?.includes(searchTerm)
  );

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
              <h1 className="text-xl font-semibold text-gray-900">Admin - Client Management</h1>
            </div>
            <div className="flex items-center space-x-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/admin/transactions')}
                className="btn-secondary flex items-center"
              >
                <Eye className="h-4 w-4 mr-2" />
                Transactions
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/admin/fraud-alerts')}
                className="btn-secondary flex items-center"
              >
                <AlertCircle className="h-4 w-4 mr-2" />
                Fraud Alerts
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/admin/rules')}
                className="btn-secondary flex items-center"
              >
                <CheckCircle className="h-4 w-4 mr-2" />
                Rules
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/dashboard')}
                className="btn-primary flex items-center"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Dashboard
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
            <AlertCircle className="h-5 w-5 text-danger-500 mr-2" />
            <span className="text-danger-700">{error}</span>
          </motion.div>
        )}

        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Client Profiles</h2>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setOpenDialog(true)}
            className="btn-primary flex items-center"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add New Client
          </motion.button>
        </div>

        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search clients by name, ID, or account number..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-10 w-full"
            />
          </div>
        </div>

        {/* Clients Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="table-container"
        >
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="table-header">Name</th>
                <th className="table-header">National ID</th>
                <th className="table-header">Account Number</th>
                <th className="table-header">Balance</th>
                <th className="table-header">User Email</th>
                <th className="table-header">Created</th>
                <th className="table-header">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredClients.map((client, index) => (
                <motion.tr
                  key={client.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="hover:bg-gray-50"
                >
                  <td className="table-cell">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {client.full_name}
                      </div>
                    </div>
                  </td>
                  <td className="table-cell">
                    <span className="font-mono text-sm">{client.national_id}</span>
                  </td>
                  <td className="table-cell">
                    <span className="font-mono text-sm">{client.bank_account_number}</span>
                  </td>
                  <td className="table-cell">
                    <span className="text-lg font-semibold text-primary-600">
                      {new Intl.NumberFormat('ar-DZ', {
                        style: 'currency',
                        currency: 'DZD',
                        minimumFractionDigits: 2
                      }).format(client.balance)}
                    </span>
                  </td>
                  <td className="table-cell">
                    <span className="text-sm text-gray-500">
                      {client.user_email || 'Not linked'}
                    </span>
                  </td>
                  <td className="table-cell text-sm text-gray-500">
                    {new Date(client.created_at).toLocaleDateString()}
                  </td>
                  <td className="table-cell">
                    <div className="flex space-x-2">
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="p-2 text-primary-600 hover:text-primary-800 hover:bg-primary-50 rounded-lg transition-colors"
                      >
                        <Eye className="h-4 w-4" />
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="p-2 text-warning-600 hover:text-warning-800 hover:bg-warning-50 rounded-lg transition-colors"
                      >
                        <Edit className="h-4 w-4" />
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="p-2 text-danger-600 hover:text-danger-800 hover:bg-danger-50 rounded-lg transition-colors"
                      >
                        <Trash2 className="h-4 w-4" />
                      </motion.button>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </motion.div>

        {filteredClients.length === 0 && (
          <div className="text-center py-12">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No clients found.</p>
          </div>
        )}

        {/* Create Client Dialog */}
        {openDialog && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md mx-4"
            >
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">Add New Client</h3>
                <button
                  onClick={() => setOpenDialog(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    First Name
                  </label>
                  <input
                    type="text"
                    value={newClient.first_name}
                    onChange={(e) => setNewClient({ ...newClient, first_name: e.target.value })}
                    className="input-field"
                    placeholder="Enter first name"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Last Name
                  </label>
                  <input
                    type="text"
                    value={newClient.last_name}
                    onChange={(e) => setNewClient({ ...newClient, last_name: e.target.value })}
                    className="input-field"
                    placeholder="Enter last name"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    National ID
                  </label>
                  <input
                    type="text"
                    value={newClient.national_id}
                    onChange={(e) => setNewClient({ ...newClient, national_id: e.target.value })}
                    className="input-field"
                    placeholder="Enter national ID"
                  />
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 mt-6">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setOpenDialog(false)}
                  className="btn-secondary"
                >
                  Cancel
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleCreateClient}
                  className="btn-primary"
                >
                  Create Client
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default Clients;
