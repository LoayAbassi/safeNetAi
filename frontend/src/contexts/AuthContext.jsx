import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        console.log('🔐 Initializing auth state...');
        const accessToken = localStorage.getItem('access_token');
        const userData = localStorage.getItem('user_data');
        
        console.log('📦 Stored tokens:', { 
          hasAccessToken: !!accessToken, 
          hasUserData: !!userData 
        });
        
        if (accessToken && userData) {
          console.log('✅ Found stored tokens, setting up auth...');
          // Set the token in axios headers
          api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
          
          // Parse user data
          const parsedUser = JSON.parse(userData);
          console.log('👤 Parsed user data:', parsedUser);
          setUser(parsedUser);
          setIsAuthenticated(true);
          console.log('✅ Auth state restored from localStorage');
        } else {
          console.log('❌ No stored tokens found');
        }
      } catch (error) {
        console.error('❌ Error initializing auth:', error);
        // Clear invalid data
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
        delete api.defaults.headers.common['Authorization'];
      } finally {
        setLoading(false);
        console.log('🏁 Auth initialization complete');
      }
    };

    initializeAuth();
  }, []);

  const refreshAuthToken = async (refreshToken) => {
    try {
      console.log('🔄 Refreshing auth token...');
      const response = await api.post('/api/auth/refresh/', { refresh: refreshToken });
      const { access } = response.data;
      
      // Update tokens
      localStorage.setItem('access_token', access);
      api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      
      console.log('✅ Token refreshed successfully');
      return true;
    } catch (error) {
      console.error('❌ Token refresh failed:', error);
      logout();
      return false;
    }
  };

  const login = async (email, password) => {
    try {
      console.log('🔐 Attempting login...');
      const response = await api.post('/api/auth/login/', { email, password });
      const { access_token, refresh_token, user: userData } = response.data;
      
      console.log('✅ Login successful, storing tokens...');
      
      // Store tokens and user data
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user_data', JSON.stringify(userData));
      
      // Set axios header
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Update state
      setUser(userData);
      setIsAuthenticated(true);
      
      console.log('✅ Auth state updated, user logged in');
      return { success: true, user: userData };
    } catch (error) {
      console.error('❌ Login failed:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await api.post('/api/auth/register/', userData);
      return { success: true, message: response.data.message };
    } catch (error) {
      console.error('❌ Registration failed:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || 'Registration failed' 
      };
    }
  };

  const verifyOTP = async (email, otp) => {
    try {
      console.log('🔐 Verifying OTP...');
      const response = await api.post('/api/auth/verify-otp/', { email, otp });
      const { access_token, refresh_token, user: userData } = response.data;
      
      console.log('✅ OTP verified, storing tokens...');
      
      // Store tokens and user data
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user_data', JSON.stringify(userData));
      
      // Set axios header
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Update state
      setUser(userData);
      setIsAuthenticated(true);
      
      console.log('✅ Auth state updated after OTP verification');
      return { success: true, user: userData };
    } catch (error) {
      console.error('❌ OTP verification failed:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || 'OTP verification failed' 
      };
    }
  };

  const logout = () => {
    console.log('🚪 Logging out, clearing tokens...');
    
    // Clear tokens and user data
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    
    // Clear axios header
    delete api.defaults.headers.common['Authorization'];
    
    // Reset state
    setUser(null);
    setIsAuthenticated(false);
    
    console.log('✅ Logout complete');
  };

  const updateUser = (newUserData) => {
    setUser(newUserData);
    localStorage.setItem('user_data', JSON.stringify(newUserData));
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    verifyOTP,
    logout,
    updateUser,
    refreshAuthToken
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
