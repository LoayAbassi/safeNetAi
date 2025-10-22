import React, { createContext, useContext, useState, useEffect } from 'react';
import i18n from '../i18n';
import api from '../api';
import { useAuth } from './AuthContext';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('en');
  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    // Get language from localStorage or browser language
    const savedLanguage = localStorage.getItem('language');
    const browserLanguage = navigator.language || navigator.userLanguage;
    
    let initialLanguage = 'en';
    
    if (savedLanguage && ['en', 'fr', 'ar'].includes(savedLanguage)) {
      initialLanguage = savedLanguage;
    } else if (browserLanguage.startsWith('fr')) {
      initialLanguage = 'fr';
    } else if (browserLanguage.startsWith('ar')) {
      initialLanguage = 'ar';
    }
    
    setLanguage(initialLanguage);
    i18n.changeLanguage(initialLanguage);
    
    // Set document direction for Arabic
    if (initialLanguage === 'ar') {
      document.documentElement.dir = 'rtl';
      document.documentElement.lang = 'ar';
    } else {
      document.documentElement.dir = 'ltr';
      document.documentElement.lang = initialLanguage;
    }
  }, []);

  const changeLanguage = async (newLanguage) => {
    if (['en', 'fr', 'ar'].includes(newLanguage)) {
      setLanguage(newLanguage);
      i18n.changeLanguage(newLanguage);
      localStorage.setItem('language', newLanguage);
      
      // Set document direction for Arabic
      if (newLanguage === 'ar') {
        document.documentElement.dir = 'rtl';
        document.documentElement.lang = 'ar';
      } else {
        document.documentElement.dir = 'ltr';
        document.documentElement.lang = newLanguage;
      }
      
      // If user is authenticated, send language preference to backend
      if (isAuthenticated && user) {
        try {
          await api.patch(`/api/users/profile/${user.id}/`, { language: newLanguage });
        } catch (error) {
          console.error('Failed to update user language preference:', error);
        }
      }
    }
  };

  const t = (key) => {
    return i18n.t(key);
  };

  const value = {
    language,
    changeLanguage,
    t
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};