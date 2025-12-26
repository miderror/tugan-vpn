import apiClient from "./apiClient";

export const fetchReferralData = async () => {
  const response = await apiClient.get("/referrals/");
  return response.data;
};
