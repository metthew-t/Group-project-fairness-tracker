import api from './axios';

export const notificationsAPI = {
  list: () => api.get('/notifications/'),
  markRead: (id) => api.put(`/notifications/${id}/mark_read/`),
  markAllRead: () => api.put('/notifications/mark-all-read/'),
};
