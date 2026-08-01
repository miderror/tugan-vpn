import axios, { type InternalAxiosRequestConfig } from "axios";
import WebApp from "@twa-dev/sdk";

let sessionKey = localStorage.getItem("session_key") || "";
let authPromise: Promise<string> | null = null;

const apiClient = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL}/api/v1`,
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (sessionKey) {
    config.headers["X-Session-Key"] = sessionKey;
  }
  return config;
});

export const ensureAuthenticated = (forceRefresh = false): Promise<string> => {
  if (sessionKey && !forceRefresh) {
    return Promise.resolve(sessionKey);
  }

  if (authPromise) {
    return authPromise;
  }

  authPromise = axios
    .post(
      `${import.meta.env.VITE_API_URL}/api/v1/auth/login`,
      {},
      { headers: { "Telegram-Init-Data": WebApp.initData } },
    )
    .then((res) => {
      const newKey = res.data.sk;
      sessionKey = newKey;
      localStorage.setItem("session_key", newKey);
      return newKey;
    })
    .finally(() => {
      authPromise = null;
    });

  return authPromise;
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const newKey = await ensureAuthenticated(true);
        originalRequest.headers["X-Session-Key"] = newKey;
        return apiClient(originalRequest);
      } catch (authError) {
        return Promise.reject(authError);
      }
    }

    return Promise.reject(error);
  },
);

export default apiClient;
