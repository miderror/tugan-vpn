import apiClient from './apiClient';

export const fetchCurrentUser = async (startParam: string | null) => {
    const params = startParam !== null ? { start_param: startParam } : {};
    const response = await apiClient.get('xui/current_user/', { params })
    return response.data;
};

export const claimGift = async () => {
    const response = await apiClient.post('xui/claim_gift/')
    return response.data;
};

export const fetchVpnConfig = async () => {
    const response = await apiClient.get('xui/vpn_config/');
    return response.data;
};