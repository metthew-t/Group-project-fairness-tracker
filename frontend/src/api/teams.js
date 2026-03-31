import api from './axios';

export const teamsAPI = {
  list: () => api.get('/teams/'),
  get: (id) => api.get(`/teams/${id}/`),
  create: (data) => api.post('/teams/', data),
  update: (id, data) => api.patch(`/teams/${id}/`, data),
  delete: (id) => api.delete(`/teams/${id}/`),
  join: (data) => api.post('/teams/join/', data),
  leave: (id) => api.post(`/teams/${id}/leave/`),
  members: (id) => api.get(`/teams/${id}/members/`),
  removeMember: (id, userId) => api.delete(`/teams/${id}/members/${userId}/`),
  promoteToLead: (id, userId) => api.post(`/teams/${id}/members/${userId}/promote/`),
};
