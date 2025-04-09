import apiClient from './apiClient';

export const fetchReferralData = async () => {
    const response = await apiClient.get('/referrals/get_referrals/');
    return response.data;
};
