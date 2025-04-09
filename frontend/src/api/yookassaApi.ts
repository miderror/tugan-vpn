import apiClient from './apiClient';

export const createPayment = async (tariffId: number, email: string) => {
  const response = await apiClient.post(
    'yookassa/create_payment/', { tariff_id: tariffId, email: email }
  );
  return response.data;
};

export const createTelegramInvoice = async (tariffId: number) => {
  const response = await apiClient.post('yookassa/create_telegram_invoice/', { tariff_id: tariffId });
  return response.data;
};