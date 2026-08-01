import apiClient from "./apiClient";
import type { UserMeApiResponse } from "@/types";

export const fetchCurrentUser = async (): Promise<UserMeApiResponse> => {
  const response = await apiClient.get<UserMeApiResponse>("/users/me");
  return response.data;
};

export const claimGift = async () => {
  const response = await apiClient.post("vpn/claim-gift/");
  return response.data;
};
