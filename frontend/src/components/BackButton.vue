<template>
  <button class="back-button" @click="goToHome">
    <span>Назад</span>
  </button>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useRouter } from 'vue-router';
import { useTwaSdk } from '@/composables/useTwaSdk';

export default defineComponent({
  name: 'BackButton',
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
.back-button {
  position: absolute;
  top: 5px;
  left: 5px;
  border-radius: 12px;
  background-color: #fff;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 4px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  border: 1px solid #dfdfdf;
  cursor: pointer;
  z-index: 10;
}

.back-button:hover {
  background-color: #f5f5f5;
}
</style>