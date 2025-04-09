import { ref } from 'vue';

export interface Notification {
  message: string;
  type?: 'info' | 'success' | 'error';
  duration?: number;
}

const currentNotification = ref<Notification | null>(null);
let timeoutId: number | null = null;

export const useNotification = () => {
  const notify = (notification: Notification) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    currentNotification.value = notification;

    timeoutId = setTimeout(() => {
      currentNotification.value = null;
      timeoutId = null;
    }, notification.duration || 3000);
  };

  return {
    currentNotification,
    notify,
  };
};