import apiClient from './apiClient';

export const fetchTariffs = async () => {
  const response = await apiClient.get('/tariffs/');
  return response.data;
};
