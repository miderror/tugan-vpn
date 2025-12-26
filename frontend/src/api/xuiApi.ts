import apiClient from "./apiClient";

export const fetchCurrentUser = async () => {
  const response = await apiClient.get("/users/me/");
  return response.data;
};

export const claimGift = async () => {
  const response = await apiClient.post("vpn/claim-gift/");
  return response.data;
};
