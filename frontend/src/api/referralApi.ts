import apiClient from './apiClient';

export const fetchReferralData = async () => {
    const response = await apiClient.get('/referrals/get_referrals/');
    return response.data;
};

export const handleReferral = async (referrerId: string) => {
    try {
        const response = await apiClient.post('/referrals/handle_referral/', {referrer_id: referrerId});
        return response.data;
    } catch (error) {}
};
