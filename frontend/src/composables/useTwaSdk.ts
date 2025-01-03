import { ref } from 'vue';
import WebApp from '@twa-dev/sdk';

export function useTwaSdk() {
  const copyToClipboard = (text: string) => {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text)
    } else {
      console.warn('API navigator.clipboard не поддерживается');
    }
  };

  const shareMessage = (message: string) => {
    const baseUrl = 'https://t.me/share/url';
    const urlParam = `url=${encodeURIComponent(message)}`;
    const textParam = `text=${encodeURIComponent('Присоединяйтесь по моей реферальной ссылке!')}`;
    const url = `${baseUrl}?${urlParam}&${textParam}`;
    WebApp.openTelegramLink(url);
  };

  const openSupportChat = () => {
    const supportUsername = import.meta.env.VITE_SUPPORT_USERNAME;
    const url = `https://t.me/${supportUsername}`;
    WebApp.openTelegramLink(url);
  };

  const getUserData = () => {
    return WebApp.initDataUnsafe.user;
  };

  const getReferrerId = () => {
    const startParam = WebApp.initDataUnsafe.start_param;
    if (startParam && /^\d+$/.test(startParam)) {
      return startParam
    }
    return null;
  };

  return {
    copyToClipboard,
    shareMessage,
    openSupportChat,
    getUserData,
    getReferrerId
  };
}