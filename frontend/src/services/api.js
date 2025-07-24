import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000'
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API calls
export const login = (credentials) => 
  api.post('/api/users/login/', credentials);

export const register = (userData) => 
  api.post('/api/users/register/', userData);

export const getProfile = () =>
  api.get('/api/users/me/');

// Dashboard API calls  
export const getAlerts = () =>
  api.get('/api/dashboard/alerts/');

export const getLogs = () =>
  api.get('/api/dashboard/logs/');

// Transaction API calls
export const submitTransaction = (data) =>
  api.post('/api/transactions/submit/', data);
