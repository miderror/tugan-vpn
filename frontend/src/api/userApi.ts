import apiClient from './apiClient';

export const fetchCurrentUser = async () => {
    const response = await apiClient.get('/users/current_user/');
    return response.data;
  };

export const fetchReferralData = async () => {
  const response = await apiClient.get('fixme/api/referral');
  return response.data;
};

export const getTelegramUserAvatar = async (userId: number): Promise<string | null> => {
  try {
    const response = await apiClient.get(`/users/${userId}/avatar/`);
    if (response.data.avatar) {
      return `data:image/jpeg;base64,${response.data.avatar}`;
    }
  } catch (error) {}
  return null;
};

export const handleReferral = async (referrerId: string) => {
  try {
    const response = await apiClient.post('/referrals/handle_referral/', { referrer_id: referrerId });
    return response.data;
  } catch (error) {}
};