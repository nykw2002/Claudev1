import axios from 'axios';
import { RuntimeJSON, AIResponse, UploadResponse } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadFiles = async (files: File[]): Promise<UploadResponse> => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  const response = await axios.post(`${API_URL}/api/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const processDocuments = async (runtimeJson: RuntimeJSON): Promise<AIResponse> => {
  const response = await api.post<AIResponse>('/api/process', runtimeJson);
  return response.data;
};

export const healthCheck = async (): Promise<any> => {
  const response = await api.get('/api/health');
  return response.data;
};

export const cleanupUploads = async (): Promise<any> => {
  const response = await api.delete('/api/upload/cleanup');
  return response.data;
};
