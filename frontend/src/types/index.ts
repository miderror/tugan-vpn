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

export interface UserMeApiResponse {
  at: string;
  ub: number;
  exp: string;
  f: number;
  ip: string;
}

export interface ReferralApiResponse {
  c: number;
  i: [number, string][];
}
