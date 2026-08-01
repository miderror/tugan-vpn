export interface TariffApiResponse {
  id: number;
  dn: string;
  dd: number;
  p: string;
  ib: boolean;
  op: string | null;
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
