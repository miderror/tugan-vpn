<template>
  <router-view />
  <Notification
    v-if="currentNotification"
    :message="currentNotification.message"
    :type="currentNotification.type"
    :duration="currentNotification.duration"
  />
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useNotification } from '@/composables/useNotification';
import Notification from '@/components/Notification.vue';

export default defineComponent({
  name: 'App',
  components: {
    Notification,
  },
  setup() {
    const { currentNotification } = useNotification();

    return {
      currentNotification,
    };
  },
});
</script>