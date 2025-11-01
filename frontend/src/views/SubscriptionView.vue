<template>
  <div class="subscription-view">
    <BackButton />
    <div class="scrollable-content">
      <h1 class="tariff-title">Тарифный план</h1>
      <TariffPlan
        v-for="plan in plans"
        :key="plan.id"
        :duration="plan.duration"
        :price-per-day="plan.pricePerDay"
        :total="plan.total"
        :original-price="plan.originalPrice"
        :is-bestseller="plan.isBestseller"
        :is-selected="selectedPlanId === plan.id"
        @select-plan="selectPlan(plan.id)"
      />
      <div class="payment-section">
        <div class="email-input">
          <input
            v-model="email"
            type="email"
            placeholder="Введите ваш email"
            enterkeyhint="done"
            @input="handleEmailInput"
            @keydown.enter="handleEnterKey"
          />
        </div>
        <button
          class="pay-button"
          :disabled="!selectedPlanId || !email"
          @click="handlePayment"
        >
          Оплатить
        </button>
      </div>
    </div>
    <DashboardButton class="dashboard-button" />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
import { useTwaSdk } from "@/composables/useTwaSdk";
import { fetchTariffs, createPayment } from "@/api";
import { useNotification } from "@/composables/useNotification";
import TariffPlan from "@/components/TariffPlan.vue";
import DashboardButton from "@/components/DashboardButton.vue";
import BackButton from "@/components/BackButton.vue";
import type { Tariff } from "@/types";

interface TariffPlan {
  id: number;
  duration: string;
  price: number;
  total: number;
  original_price?: number;
  is_bestseller: boolean;
}

export default defineComponent({
  name: "SubscriptionView",
  components: {
    TariffPlan,
    DashboardButton,
    BackButton,
  },
  setup() {
    const { openExternalLink, hapticFeedback } = useTwaSdk();
    const { notify } = useNotification();

    const selectedPlanId = ref<number | null>();

    const plans = ref<Tariff[]>([]);
    const email = ref<string>("");

    onMounted(async () => {
      try {
        plans.value = await fetchTariffs();
      } catch (error) {}
    });

    const validateEmail = (email: string) => {
      const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return regex.test(email);
    };

    const selectPlan = (planId: number) => {
      selectedPlanId.value = planId;
    };

    const handleEmailInput = (event: Event) => {
      const target = event.target as HTMLInputElement;
      email.value = target.value;
    };

    const handleEnterKey = (event: KeyboardEvent) => {
      const emailInput = event.target as HTMLInputElement;
      emailInput.blur();
    };

    const handlePayment = async () => {
      if (!selectedPlanId.value) {
        hapticFeedback("error");
        notify({ message: "Выберите тарифный план", type: "error" });
        return;
      }

      if (!email.value || !validateEmail(email.value)) {
        hapticFeedback("error");
        notify({ message: "Введите корректный email", type: "error" });
        return;
      }

      hapticFeedback("success");
      try {
        const payment = await createPayment(selectedPlanId.value, email.value);

        if (payment.payment_url) {
          openExternalLink(payment.payment_url);
        }
      } catch (error) {
        notify({ message: "Ошибка при создании платежа", type: "error" });
      }
    };

    return {
      plans,
      selectedPlanId,
      email,
      selectPlan,
      handleEmailInput,
      handleEnterKey,
      handlePayment,
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
  margin-bottom: 20px;
}

.payment-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: auto;
  padding-top: 20px;
}

.email-input {
  width: 100%;
  max-width: 100%;
}

.email-input input {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border: 1px solid #eaeaea;
  border-radius: 12px;
  outline: none;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.email-input input:focus {
  border-color: #007bff;
}

.pay-button {
  width: 100%;
  padding: 14px;
  font-size: 16px;
  font-weight: 600;
  background-color: #2d5009;
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  box-sizing: border-box;
}

.pay-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.pay-button:not(:disabled):hover {
  background-color: #3a660b;
}

.dashboard-button {
  flex-shrink: 0;
  margin-top: auto;
}
</style>
