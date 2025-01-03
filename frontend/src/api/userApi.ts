import apiClient from './apiClient';

export const fetchCurrentUser = async () => {
    const response = await apiClient.get('/users/current_user/');
    return response.data;
};

export const getTelegramUserAvatar = (userId: number): string => {
    return `${import.meta.env.VITE_API_URL}users/${userId}/avatar/`;
};
