import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
const readIntent = import.meta.env.VITE_API_READ_INTENT ?? 'READ';

export const apiClient = axios.create({
  baseURL,
  headers: {
    'X-Intent': readIntent,
  },
});

export function writeHeaders() {
  const headers: Record<string, string> = { 'X-Intent': 'WRITE' };
  const apiKey = import.meta.env.VITE_KERNEL_API_KEY;
  if (apiKey) {
    headers['X-API-KEY'] = apiKey;
  }
  return headers;
}
