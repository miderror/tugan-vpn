import apiClient from './apiClient';

export const getTelegramUserAvatar = (userId: number): (() => Promise<string | null>) => {
    return async () => {
        try {
            const response = await apiClient.get(`/users/${userId}/avatar/`, {
                responseType: 'blob',
            });
            if (response.status === 200) {
                return URL.createObjectURL(response.data);
            }
        } catch (error) {}
        return null;
    };
};

export const getUserIp = async () => {
    const response = await apiClient.get('/get_user_ip/');
    return response.data;
  };