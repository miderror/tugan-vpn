import apiClient from "./apiClient";
import type { Tariff, TariffApiResponse } from "@/types";

const mapApiDataToTariff = (apiTariff: TariffApiResponse): Tariff => {
  const totalPrice = parseFloat(apiTariff.p);

  return {
    id: apiTariff.id,
    duration: apiTariff.dn,
    total: totalPrice,
    pricePerDay: Math.trunc((totalPrice / apiTariff.dd) * 10) / 10,
    originalPrice: apiTariff.op ? parseFloat(apiTariff.op) : undefined,
    isBestseller: apiTariff.ib,
  };
};

export const fetchTariffs = async (): Promise<Tariff[]> => {
  const response = await apiClient.get<TariffApiResponse[]>("/billing/tariffs");
  return response.data.map(mapApiDataToTariff);
};

export const createPayment = async (tariffId: number, email: string) => {
  const response = await apiClient.post<{ url: string }>(
    "/billing/create_payment",
    {
      tid: tariffId,
      em: email,
    },
  );
  return { payment_url: response.data.url };
};
