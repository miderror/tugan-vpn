<template>
  <div v-if="currentNotification" class="notification" :class="currentNotification.type">
    {{ currentNotification.message }}
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useNotification } from '@/composables/useNotification';

export default defineComponent({
  name: 'Notification',
  setup() {
    const { currentNotification } = useNotification();

    return {
      currentNotification,
    };
  },
});
</script>

<style scoped>
.notification {
  position: fixed;
  bottom: 12%;
  left: 50%;
  transform: translateX(-50%);
  padding: 10px 12px;
  border-radius: 8px;
  color: #f0f0f0;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  font-size: 14px;
  z-index: 1000;
  opacity: 0.95;
  transition: opacity 0.3s ease;
  text-align: center;
}

.notification.info {
  background-color: #333;
}

.notification.success {
  background-color: #4caf50;
}

.notification.error {
  background-color: #f44336;
}
</style>