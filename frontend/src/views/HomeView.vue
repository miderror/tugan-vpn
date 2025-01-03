<template>
  <div class="dashboard-card">
    <div class="dashboard-content">
      <div class="user-section">
        <SvgIcon :iconName="'logo'" class="logo" />
        <div class="user-header">
          <div class="welcome-text">Привет, {{ user.first_name }}</div>
          <SvgIcon :iconName="'user-icon'" class="user-icon" />
        </div>
        <div class="stats-container">
          <StatsBox label="Использовано" :value="usage" />
          <StatsBox label="Подписка до" :value="subscriptionDate" />
        </div>
      </div>
      <div class="buttons-container">
        <div class="action-buttons">
          <ActionButton
            iconName="vpn-icon"
            altText="VPN Connection Icon"
            text="Подключиться к VPN"
            @click="goToVpn"
          />
          <ActionButton
            iconName="subscription-icon"
            altText="Subscription Icon"
            text="Оформить подписку"
            @click="goToSubscription"
          />
          <ActionButton
            iconName="support-icon"
            altText="Support Icon"
            text="Тех. поддержка"
            @click="openSupport"
          />
          <ActionButton
            iconName="referral-icon"
            altText="Referral Program Icon"
            text="Реферальная программа"
            @click="goToReferral"
          />
        </div>
        <div class="promo-button">
          <PromoButton
            iconName="trial-access-icon"
            altText="Trial Access Icon"
            text="Получить доступ на 7 дней"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useTwaSdk } from '@/composables/useTwaSdk';
import { handleReferral } from '@/api';
import StatsBox from '@/components/StatsBox.vue';
import ActionButton from '@/components/ActionButton.vue';
import PromoButton from '@/components/PromoButton.vue';
import SvgIcon from '@/components/SvgIcon.vue';

export default defineComponent({
  name: 'HomeView',
  components: {
    StatsBox,
    ActionButton,
    PromoButton,
    SvgIcon,
  },
  setup() {
    const router = useRouter();
    const { openSupportChat, getUserData, getReferrerId } = useTwaSdk();

    const user = ref<{ first_name?: string }>({ first_name: 'user' });
    const usage = ref('36.02/500.0 GB');
    const subscriptionDate = ref('17.12.2025');

    onMounted(async () => {
      const userData = getUserData();
      if (userData?.first_name) {
        user.value.first_name = userData.first_name;
      }

      const referrerId = getReferrerId();
      if (referrerId) {
        await handleReferral(referrerId);
  }
    });

    const goToVpn = () => {
      router.push({ name: 'vpn' });
    };

    const goToSubscription = () => {
      router.push({ name: 'subscription' });
    };

    const goToReferral = () => {
      router.push({ name: 'referral' });
    };

    const openSupport = () => {
      openSupportChat();
    };

    return {
      user,
      usage,
      subscriptionDate,
      goToVpn,
      goToSubscription,
      goToReferral,
      openSupport,
    };
  },
});
</script>

<style scoped>
.dashboard-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 100vh;
  max-width: 400px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 700px;
  gap: 20px;
}

.logo {
  width: 250px;
  height: auto;
  align-self: center;
  margin-bottom: 10px;
}

.user-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  color: rgb(18, 18, 18);
  font-weight: 600;
  max-width: 100%;
}

.welcome-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.user-icon {
  flex-shrink: 0;
}

.stats-container {
  display: flex;
  gap: 8px;
  width: 100%;
  flex-shrink: 1
}

.stats-container .stats-box {
  height: auto;
  gap: 5px;
}

.buttons-container {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>