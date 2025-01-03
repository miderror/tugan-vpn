<template>
  <div class="subscription-view">
    <BackButton />
    <div class="scrollable-content">
      <h1 class="tariff-title">Тарифный план</h1>
      <TariffPlan
        v-for="plan in plans"
        :key="plan.id"
        :duration="plan.duration"
        :price="plan.price"
        :total="plan.total"
        :originalPrice="plan.originalPrice"
        :isBestseller="plan.isBestseller"
        :isSelected="selectedPlanId === plan.id"
        @select-plan="selectPlan(plan.id)"
      />
    </div>
    <DashboardButton class="dashboard-button" />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useRouter } from 'vue-router';
import TariffPlan from '@/components/TariffPlan.vue';
import DashboardButton from '@/components/DashboardButton.vue';
import BackButton from '@/components/BackButton.vue';

export default defineComponent({
  name: 'SubscriptionView',
  components: {
    TariffPlan,
    DashboardButton,
    BackButton,
  },
  setup() {
    const router = useRouter();
    const selectedPlanId = ref<number | null>();

    const plans = ref([
      {
        id: 1,
        duration: '1 месяц',
        price: 7,
        total: 210,
        originalPrice: undefined,
        isBestseller: false,
      },
      {
        id: 2,
        duration: '3 месяца',
        price: 6.5,
        total: 585,
        originalPrice: 700,
        isBestseller: true,
      },
      {
        id: 3,
        duration: '6 месяцев',
        price: 6,
        total: 1080,
        originalPrice: 1200,
        isBestseller: false,
      },
      {
        id: 4,
        duration: '12 месяцев',
        price: 5.5,
        total: 2007,
        originalPrice: 2200,
        isBestseller: false,
      },
    ]);

    const selectPlan = (planId: number) => {
      selectedPlanId.value = planId;
    };

    return {
      plans,
      selectedPlanId,
      selectPlan,
    };
  },
});
</script>

<style scoped>
.subscription-view {
  max-width: 480px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: 100vh;
  box-sizing: border-box;
}

.scrollable-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding-bottom: 20px;
}

.tariff-title {
  color: #121212;
  font-size: 26px;
  font-weight: 600;
  line-height: 31px;
  text-align: center;
}

.dashboard-button {
  flex-shrink: 0;
  margin-top: auto;
}
</style>