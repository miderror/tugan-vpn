<template>
  <button class="dashboard-button" @click="goToHome">
    <SvgIcon :iconName="'dashboard-icon'" class="dashboard-icon" />
    <span>Личный кабинет</span>
  </button>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useRouter } from 'vue-router';
import { useTwaSdk } from '@/composables/useTwaSdk';
import SvgIcon from './SvgIcon.vue';

export default defineComponent({
  name: 'DashboardButton',
  components: {
    SvgIcon,
  },
  setup() {
    const { hapticFeedback } = useTwaSdk();
    const router = useRouter();

    const goToHome = () => {
      hapticFeedback('success');
      router.push({ name: 'home' });
    };

    return {
      goToHome,
    };
  },
});
</script>

<style scoped>
.dashboard-button {
  border-radius: 12px;
  background-color: #fff;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px 32px;
  border: 1px solid #dfdfdf;
  cursor: pointer;
  width: 100%;
}

.dashboard-icon {
  width: 24px;
  height: 24px;
}
</style>