import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Send, 
  MapPin, 
  CreditCard, 
  DollarSign, 
  User,
  AlertCircle,
  CheckCircle,
  Loader,
  Shield
} from 'lucide-react';
import api from '../api';
import OTPVerification from '../components/OTPVerification';
import { useTranslation } from 'react-i18next';

const Transfer = () => {
  const [formData, setFormData] = useState({
    amount: '',
    transaction_type: 'transfer',
    to_account_number: '',
  });
  const [currentLocation, setCurrentLocation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showOTP, setShowOTP] = useState(false);
  const [pendingTransaction, setPendingTransaction] = useState(null);
  const navigate = useNavigate();
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
    getCurrentLocation();
  }, []);

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCurrentLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (error) => {
          setError('Location access is required for secure transactions. Please enable location services and refresh the page.');
          setCurrentLocation({ lat: 0, lng: 0 });
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 300000 // 5 minutes
        }
      );
    } else {
      setCurrentLocation({ lat: 0, lng: 0 });
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const transactionData = {
        ...formData,
        current_location: currentLocation,
        device_fingerprint: 'web-' + Date.now(), // Simple device fingerprint
      };

      const response = await api.post('/api/client/transactions/', transactionData);
      
      if (response.data.requires_otp) {
        // Transaction requires OTP verification
        setPendingTransaction(response.data);
        setShowOTP(true);
        
        // Enhanced message for distance violations
        if (response.data.distance_violation) {
          setSuccess('⚠️ SECURITY ALERT: Transaction location is far from your home address. OTP verification is mandatory for your protection.');
        } else {
          setSuccess('Transaction created. Please verify with the OTP sent to your email.');
        }
      } else if (response.data.status === 'pending') {
        setSuccess(`Transaction created but flagged for review. Risk Score: ${response.data.risk_score}. Please check your email for approval.`);
        // Reset form
        setFormData({
          amount: '',
          transaction_type: 'transfer',
          to_account_number: '',
        });
      } else {
        setSuccess(`Transaction completed successfully! Risk Score: ${response.data.risk_score}`);
        // Reset form
        setFormData({
          amount: '',
          transaction_type: 'transfer',
          to_account_number: '',
        });
      }
      
    } catch (error) {
      if (error.response?.data) {
        if (typeof error.response.data === 'object') {
          const errorMessages = Object.values(error.response.data).flat();
          setError(errorMessages.join(', '));
        } else {
          setError(error.response.data);
        }
      } else {
        setError('Failed to create transaction');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleOTPSuccess = (data) => {
    setShowOTP(false);
    setPendingTransaction(null);
    setSuccess(`Transaction completed successfully after OTP verification! Risk Score: ${data.risk_score || 'N/A'}`);
    
    // Reset form
    setFormData({
      amount: '',
      transaction_type: 'transfer',
      to_account_number: '',
    });
    
    // Navigate back to dashboard after a delay
    setTimeout(() => {
      navigate('/client-dashboard');
    }, 3000);
  };

  const handleOTPCancel = () => {
    setShowOTP(false);
    setPendingTransaction(null);
    setError('Transaction cancelled. You can try again.');
  };

  const handleOTPResend = () => {
    setSuccess('OTP resent successfully. Please check your email.');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-md mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="bg-white rounded-lg shadow-lg p-8"
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/client-dashboard')}
              className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="h-5 w-5 mr-2" />
              {t('back_to_dashboard')}
            </motion.button>
            <h1 className="text-2xl font-bold text-gray-900">{t('transfer')}</h1>
          </div>

          {/* Security Notice */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg"
          >
            <div className="flex items-center">
              <Shield className="h-5 w-5 text-blue-500 mr-2" />
              <span className="text-blue-800 text-sm font-medium">{t('security_notice')}</span>
            </div>
            <p className="text-blue-700 text-xs mt-1">
              {t('high_risk_transactions')}
            </p>
          </motion.div>

          {/* Alerts */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center"
            >
              <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
              <span className="text-red-700">{error}</span>
            </motion.div>
          )}

          {success && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center"
            >
              <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
              <span className="text-green-700">{success}</span>
            </motion.div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Transaction Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('transaction_type')}
              </label>
              <select
                name="transaction_type"
                value={formData.transaction_type}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="deposit">{t('deposit')}</option>
                <option value="withdraw">{t('withdraw')}</option>
                <option value="transfer">{t('transfer')}</option>
              </select>
            </div>

            {/* Amount */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('amount_dzd')}
              </label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="number"
                  name="amount"
                  value={formData.amount}
                  onChange={handleChange}
                  required
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>

            {/* Recipient Account (for transfers) */}
            {formData.transaction_type === 'transfer' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                transition={{ duration: 0.3 }}
              >
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('recipient_account')}
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    name="to_account_number"
                    value={formData.to_account_number}
                    onChange={handleChange}
                    required
                    placeholder="Enter account number"
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
              </motion.div>
            )}

            {/* Enhanced Location Info */}
            <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
              <div className="flex items-center mb-2">
                <MapPin className="h-5 w-5 text-blue-600 mr-2" />
                <span className="text-sm font-medium text-blue-900">{t('location_security')}</span>
              </div>
              
              {currentLocation ? (
                <div>
                  <div className="flex items-center text-sm text-blue-700 mb-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                    <span className="font-medium">{t('location_verified')}</span>
                  </div>
                  <p className="text-xs text-blue-600 mb-2">
                    {t('coordinates')}: {currentLocation.lat.toFixed(4)}, {currentLocation.lng.toFixed(4)}
                  </p>
                  <div className="bg-blue-100 rounded p-2">
                    <p className="text-xs text-blue-800">
                      🔒 {t('location_protection')}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="flex items-center text-sm text-amber-700">
                  <div className="w-2 h-2 bg-amber-500 rounded-full mr-2 animate-pulse"></div>
                  <span>{t('getting_location')}</span>
                </div>
              )}
            </div>

            {/* Submit Button */}
            <motion.button
              type="submit"
              disabled={loading || !currentLocation}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full btn-primary flex items-center justify-center py-3"
            >
              {loading ? (
                <Loader className="h-5 w-5 animate-spin mr-2" />
              ) : (
                <Send className="h-5 w-5 mr-2" />
              )}
              {loading ? t('processing') : t('create_transaction')}
            </motion.button>
          </form>
        </motion.div>
      </div>

      {/* OTP Verification Modal */}
      {showOTP && pendingTransaction && (
        <OTPVerification
          transactionId={pendingTransaction.transaction_id}
          onSuccess={handleOTPSuccess}
          onCancel={handleOTPCancel}
          onResend={handleOTPResend}
        />
      )}
    </div>
  );
};

export default Transfer;
