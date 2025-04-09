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

  const getStartParam = () => {
    return WebApp.initDataUnsafe.start_param || null;
  };
  
  const openDownloadPageFromSdk = () => {
    const platform = WebApp.platform;
    console.log(WebApp)

    if (platform === 'android') {
      window.open(import.meta.env.VITE_APP_PLAYSTORE_URL, '_blank');
    } else if (platform === 'ios') {
      window.open(import.meta.env.VITE_APP_APPSTORE_URL, '_blank');
    } else {
      window.open(import.meta.env.VITE_APP_DOWNLOAD_PAGE, '_blank');
    }
  };

  const openExternalLink = (url: string) => {
    WebApp.openLink(url);
  };

  const openSubscriptionLink = (subscriptionUrl: string): void => {
    const platform = WebApp.platform;
    let appUrl: string;

    if (platform === 'ios') {
      appUrl = `streisand://import/${subscriptionUrl}#TUGANVPN`;
    } else if (platform == 'android') {
      appUrl = `v2raytun://import/${encodeURIComponent(subscriptionUrl)}`;
    } else {
      appUrl = `hiddify://import/${subscriptionUrl}`;
    }

    window.open(appUrl, '_blank');
  };

  const openRulesetLink = (rulesetUrl: string): void => {
    const platform = WebApp.platform;
    let appUrl: string;

    if (platform === 'ios') {
      appUrl = `streisand://aW1wb3J0L3JvdXRlOi8vWW5Cc2FYTjBNRERWQVFJREJBVUdEQjhnSVZWeWRXeGxjMTFrYjIxaGFXNU5ZWFJqYUdWeVZHNWhiV1ZlWkc5dFlXbHVVM1J5WVhSbFozbFVkWFZwWktNSEVSWFVDQWtLQ3d3TkRoQmRaRzl0WVdsdVRXRjBZMmhsY2xaa2IyMWhhVzVTYVhCYmIzVjBZbTkxYm1SVVlXZFdiR2x1WldGeW9LRVBXR2RsYjJsd09uSjFWbVJwY21WamROSVNDUkFUVzI5MWRHSnZkVzVrVkdGbm9SUmVjbVZuWlhod09pNHFYQzV5ZFNUVEZoY0pFQmdaVzI5MWRHSnZkVzVrVkdGblhXUnZiV0ZwYmsxaGRHTm9aWEpXYUhsaWNtbGtwUm9iSEIwZVh4QVFaMlZ2YzJsMFpUcDBaV3hsWjNKaGJWOFFFR2RsYjNOcGRHVTZkMmhoZEhOaGNIQmRaMlZ2YzJsMFpUcGhjSEJzWlY1blpXOXphWFJsT21kdmIyZHNaVjVuWlc5emFYUmxPbWwwZFc1bGMyMEFVZ0JWQUMwQVJBQnBBSElBWlFCakFIVFlQTjMzMkR6ZCtscEpVRTl1UkdWdFlXNWtYeEFrUXpRelFrVTVSRGt0T0RGQk15MDBRamhGTFRrM1JrTXRPRFE0TlVFNFJqZENRelkyQUFnQUV3QVpBQ2NBTEFBN0FFQUFSQUJOQUZzQVlnQmxBSEVBZUFCNUFIc0FoQUNMQUpBQW5BQ2VBSzBBdEFEQUFNNEExUURiQU80QkFRRVBBUjRCTFFGSUFWTUFBQUFBQUFBQ0FRQUFBQUFBQUFBaUFBQUFBQUFBQUFBQUFBQUFBQUFCZWc9PQ==`;
    } else if (platform == 'android') {
      appUrl = `v2raytun://import-ruleset/${encodeURIComponent(rulesetUrl)}`;
    } else {
      appUrl = `hiddify://aW1wb3J0L3JvdXRlOi8vWW5Cc2FYTjBNRERWQVFJREJBVUdEQjhnSVZWeWRXeGxjMTFrYjIxaGFXNU5ZWFJqYUdWeVZHNWhiV1ZlWkc5dFlXbHVVM1J5WVhSbFozbFVkWFZwWktNSEVSWFVDQWtLQ3d3TkRoQmRaRzl0WVdsdVRXRjBZMmhsY2xaa2IyMWhhVzVTYVhCYmIzVjBZbTkxYm1SVVlXZFdiR2x1WldGeW9LRVBXR2RsYjJsd09uSjFWbVJwY21WamROSVNDUkFUVzI5MWRHSnZkVzVrVkdGbm9SUmVjbVZuWlhod09pNHFYQzV5ZFNUVEZoY0pFQmdaVzI5MWRHSnZkVzVrVkdGblhXUnZiV0ZwYmsxaGRHTm9aWEpXYUhsaWNtbGtwUm9iSEIwZVh4QVFaMlZ2YzJsMFpUcDBaV3hsWjNKaGJWOFFFR2RsYjNOcGRHVTZkMmhoZEhOaGNIQmRaMlZ2YzJsMFpUcGhjSEJzWlY1blpXOXphWFJsT21kdmIyZHNaVjVuWlc5emFYUmxPbWwwZFc1bGMyMEFVZ0JWQUMwQVJBQnBBSElBWlFCakFIVFlQTjMzMkR6ZCtscEpVRTl1UkdWdFlXNWtYeEFrUXpRelFrVTVSRGt0T0RGQk15MDBRamhGTFRrM1JrTXRPRFE0TlVFNFJqZENRelkyQUFnQUV3QVpBQ2NBTEFBN0FFQUFSQUJOQUZzQVlnQmxBSEVBZUFCNUFIc0FoQUNMQUpBQW5BQ2VBSzBBdEFEQUFNNEExUURiQU80QkFRRVBBUjRCTFFGSUFWTUFBQUFBQUFBQ0FRQUFBQUFBQUFBaUFBQUFBQUFBQUFBQUFBQUFBQUFCZWc9PQ==`;
    }

    window.open(appUrl, '_blank');
  };

  const hapticFeedback = (style: 'error' | 'success' | 'warning') => {
    WebApp.HapticFeedback.notificationOccurred('warning');
  };

  return {
    copyToClipboard,
    shareMessage,
    openSupportChat,
    getUserData,
    getStartParam,
    openDownloadPageFromSdk,
    openExternalLink,
    openSubscriptionLink,
    openRulesetLink,
    hapticFeedback,
  };
}