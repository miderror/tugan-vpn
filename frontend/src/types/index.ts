export interface TariffApiResponse {
  id: number;
  display_name: string;
  duration_days: number;
  price: string;
  is_bestseller: boolean;
  original_price: string | null;
}

export interface Tariff {
  id: number;
  duration: string;
  pricePerDay: number;
  total: number;
  originalPrice?: number;
  isBestseller: boolean;
}
