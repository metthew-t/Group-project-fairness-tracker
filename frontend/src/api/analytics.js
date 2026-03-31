import api from './axios';

export const analyticsAPI = {
  team: (teamId) => api.get(`/analytics/team/${teamId}/`),
  project: (projectId) => api.get(`/analytics/project/${projectId}/`),
  exportCSV: (teamId) => api.get(`/analytics/${teamId}/export-csv/`, { responseType: 'blob' }),
};
