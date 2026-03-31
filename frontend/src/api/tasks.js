import api from './axios';

export const tasksAPI = {
  list: () => api.get('/tasks/'),
  get: (id) => api.get(`/tasks/${id}/`),
  create: (data) => api.post('/tasks/', data),
  update: (id, data) => api.patch(`/tasks/${id}/`, data),
  delete: (id) => api.delete(`/tasks/${id}/`),
  assign: (id, userIds) => api.post(`/tasks/${id}/assign/`, { user_ids: userIds }),
  unassign: (id, userIds) => api.post(`/tasks/${id}/unassign/`, { user_ids: userIds }),
};
