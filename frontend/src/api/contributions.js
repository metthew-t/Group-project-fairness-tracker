import api from './axios';

export const contributionsAPI = {
  list: () => api.get('/contributions/'),
  create: (formData) => api.post('/contributions/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  verify: (id, data) => api.post(`/contributions/${id}/verify/`, data),
  lead_action: (id, data) => api.post(`/contributions/${id}/lead_action/`, data),
  peers: () => api.get('/contributions/peers/'),
};
