import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000',
  // Fail visibly if the local API is unavailable instead of leaving the UI
  // on an endless loading screen.
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to attach the JWT token to every request
api.interceptors.request.use((config) => {
  const token = typeof window === 'undefined' ? null : localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default api;

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (!axios.isAxiosError(error)) return fallback;

  const detail = error.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (error.code === 'ERR_NETWORK') {
    return 'Cannot reach the backend at 127.0.0.1:8000. Make sure the Python server is running.';
  }
  return error.message || fallback;
}
