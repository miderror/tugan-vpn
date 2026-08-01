import apiClient from "./apiClient";
import type { ReferralApiResponse } from "@/types";

export const fetchReferralData = async (): Promise<ReferralApiResponse> => {
  const response = await apiClient.get<ReferralApiResponse>("/users/referrals");
  return response.data;
};
