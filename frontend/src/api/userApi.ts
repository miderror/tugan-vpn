import apiClient from './apiClient';

export const fetchCurrentUser = async () => {
    const response = await apiClient.get('/users/current_user/');
    return response.data;
};

// export const getTelegramUserAvatar = (userId: number): string => {
//     return `${import.meta.env.VITE_API_URL}users/${userId}/avatar/`;
// };

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