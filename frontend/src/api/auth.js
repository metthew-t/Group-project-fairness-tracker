import api from './axios';

export const authAPI = {
  login: (data) => api.post('/auth/login/', data),
  register: (data) => api.post('/auth/register/', data),
  sendVerification: () => api.post('/auth/send-verification/'),
  verifyEmail: (code) => api.post('/auth/verify-email/', { code }),
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};
