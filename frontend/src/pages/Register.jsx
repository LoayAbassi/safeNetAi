import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  User, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  CreditCard, 
  IdCard, 
  AlertCircle,
  CheckCircle,
  MapPin,
  Loader
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    national_id: '',
    bank_account_number: '',
  });
  const [currentLocation, setCurrentLocation] = useState(null);
  const [locationLoading, setLocationLoading] = useState(true);
  const [locationError, setLocationError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    getCurrentLocation();
  }, []);

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const location = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };
          setCurrentLocation(location);
          setLocationLoading(false);
          console.log('Location captured for registration:', location);
        },
        (error) => {
          console.error('Geolocation error during registration:', error);
          setLocationError('Location access denied. You can still register, but location-based security features will be limited.');
          setCurrentLocation({ lat: 0, lng: 0 }); // Fallback coordinates
          setLocationLoading(false);
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 300000 // 5 minutes
        }
      );
    } else {
      setLocationError('Geolocation is not supported by this browser.');
      setCurrentLocation({ lat: 0, lng: 0 });
      setLocationLoading(false);
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

    // Validate passwords match
    if (formData.password !== formData.password_confirm) {
      setError('Passwords do not match');
      return;
    }

    // Validate password length
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    // Ensure location is captured
    if (!currentLocation) {
      setError('Location access is required for enhanced security. Please allow location access and try again.');
      return;
    }

    setLoading(true);

    // Include location data in registration
    const registrationData = {
      ...formData,
      registration_location: currentLocation
    };

    const result = await register(registrationData);
    
    if (result.success) {
      // Redirect to OTP verification
      navigate('/verify-otp', { 
        state: { 
          email: formData.email,
          message: 'Registration successful! Please check your email for OTP verification.'
        }
      });
    } else {
      if (typeof result.error === 'object') {
        // Handle field-specific errors
        const errorMessages = Object.values(result.error).flat();
        setError(errorMessages.join(', '));
      } else {
        setError(result.error);
      }
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 py-12 px-4 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-2xl w-full space-y-8"
      >
        <div className="text-center">
          <motion.h2
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-3xl font-bold text-gray-900"
          >
            Create Your SafeNetAi Account
          </motion.h2>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="mt-2 text-sm text-gray-600"
          >
            Join our secure banking platform with AI-powered fraud detection
          </motion.p>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-lg shadow-xl p-8"
        >
          {error && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mb-6 p-4 bg-danger-50 border border-danger-200 rounded-lg flex items-center"
            >
              <AlertCircle className="h-5 w-5 text-danger-500 mr-2" />
              <span className="text-danger-700 text-sm">{error}</span>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* First Name */}
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-2">
                  First Name
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="first_name"
                    name="first_name"
                    type="text"
                    required
                    className="input-field pl-10"
                    placeholder="Enter first name"
                    value={formData.first_name}
                    onChange={handleChange}
                  />
                </div>
              </div>

              {/* Last Name */}
              <div>
                <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-2">
                  Last Name
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="last_name"
                    name="last_name"
                    type="text"
                    required
                    className="input-field pl-10"
                    placeholder="Enter last name"
                    value={formData.last_name}
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  className="input-field pl-10"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* National ID */}
              <div>
                <label htmlFor="national_id" className="block text-sm font-medium text-gray-700 mb-2">
                  National ID
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <IdCard className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="national_id"
                    name="national_id"
                    type="text"
                    required
                    className="input-field pl-10"
                    placeholder="Enter national ID"
                    value={formData.national_id}
                    onChange={handleChange}
                  />
                </div>
              </div>

              {/* Bank Account Number */}
              <div>
                <label htmlFor="bank_account_number" className="block text-sm font-medium text-gray-700 mb-2">
                  Bank Account Number
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <CreditCard className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="bank_account_number"
                    name="bank_account_number"
                    type="text"
                    required
                    className="input-field pl-10"
                    placeholder="Enter account number"
                    value={formData.bank_account_number}
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  className="input-field pl-10 pr-10"
                  placeholder="Enter password"
                  value={formData.password}
                  onChange={handleChange}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
              <p className="mt-1 text-sm text-gray-500">Password must be at least 8 characters long</p>
            </div>

            {/* Confirm Password */}
            <div>
              <label htmlFor="password_confirm" className="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password_confirm"
                  name="password_confirm"
                  type={showConfirmPassword ? 'text' : 'password'}
                  required
                  className="input-field pl-10 pr-10"
                  placeholder="Confirm your password"
                  value={formData.password_confirm}
                  onChange={handleChange}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
            </div>

            {/* Location Information */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center mb-2">
                <MapPin className="h-5 w-5 text-blue-600 mr-2" />
                <h3 className="text-sm font-medium text-blue-900">Location Security</h3>
              </div>
              
              {locationLoading ? (
                <div className="flex items-center text-sm text-blue-700">
                  <Loader className="h-4 w-4 animate-spin mr-2" />
                  <span>Getting your location for enhanced security...</span>
                </div>
              ) : currentLocation ? (
                <div>
                  <p className="text-sm text-blue-700 mb-1">
                    Location captured successfully for home address setup.
                  </p>
                  <p className="text-xs text-blue-600">
                    Coordinates: {currentLocation.lat.toFixed(4)}, {currentLocation.lng.toFixed(4)}
                  </p>
                </div>
              ) : (
                <div className="text-sm text-red-600">
                  <p>❌ Location not available</p>
                  {locationError && <p className="text-xs mt-1">{locationError}</p>}
                </div>
              )}
              
              <p className="text-xs text-blue-600 mt-2">
                Your location will be used to set up your home address for fraud detection.
                This helps protect your account from unauthorized access.
              </p>
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading || locationLoading}
              className="btn-primary w-full flex justify-center items-center py-3"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <>
                  <CheckCircle className="h-5 w-5 mr-2" />
                  Create Account
                </>
              )}
            </motion.button>
          </form>

          <div className="mt-6 text-center">
            <Link
              to="/login"
              className="text-primary-600 hover:text-primary-500 text-sm font-medium transition-colors duration-200"
            >
              Already have an account? Sign In
            </Link>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default Register;
