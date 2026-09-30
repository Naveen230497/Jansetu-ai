import axios from 'axios';

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/api'
});

export const getRequests = (filters = {}) => api.get('/requests', { params: filters }).then(res => res.data);
export const getDistricts = () => api.get('/districts').then(res => res.data);
export const getPriorities = () => api.get('/priorities').then(res => res.data);
export const getStats = () => api.get('/stats').then(res => res.data);
export const submitText = (text) => api.post('/submit-text', { text }).then(res => res.data);
export const submitVoice = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/submit-voice', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }).then(res => res.data);
};
export const generateBrief = () => api.post('/generate-brief', {}, { responseType: 'blob' }).then(res => res.data);
export const recalculate = () => api.post('/recalculate').then(res => res.data);
