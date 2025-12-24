import apiClient from "./apiClient";

export const fetchCurrentUser = async () => {
  const response = await apiClient.get("/users/me/");
  return response.data;
};

export const claimGift = async () => {
  const response = await apiClient.post("xui/claim_gift/");
  return response.data;
};

export const fetchVpnConfig = async () => {
  const response = await apiClient.get("/vpn/config/");
  return response.data;
};
