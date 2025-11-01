import apiClient from "./apiClient";
import type { Tariff, TariffApiResponse } from "@/types";

const mapApiDataToTariff = (apiTariff: TariffApiResponse): Tariff => {
  const totalPrice = parseFloat(apiTariff.price);

  return {
    id: apiTariff.id,
    duration: apiTariff.display_name,
    total: totalPrice,
    pricePerDay: Math.trunc((totalPrice / apiTariff.duration_days) * 10) / 10,
    originalPrice: apiTariff.original_price
      ? parseFloat(apiTariff.original_price)
      : undefined,
    isBestseller: apiTariff.is_bestseller,
  };
};

export const fetchTariffs = async (): Promise<Tariff[]> => {
  const response = await apiClient.get<TariffApiResponse[]>("/tariffs/");
  return response.data.map(mapApiDataToTariff);
};
