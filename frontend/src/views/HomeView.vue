<template>
  <div class="dashboard-card">
    <div class="dashboard-content">
      <div class="user-section">
        <SvgIcon :iconName="'logo'" class="logo" />
        <div class="user-header">
          <div class="welcome-text">Привет, {{ user.first_name }}</div>
          <SvgIcon :iconName="'user-icon'" class="user-icon" />
        </div>

        <div class="ip-box">
          <StatsBox label="Ваш IP:" :value="userIp" />
        </div>

        <div class="stats-container">
          <StatsBox label="Использовано:" :value="usage" />
          <StatsBox label="Подписка до:" :value="subscriptionDate" />
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
            @click="claimGiftHandler"
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
import { claimGift, fetchCurrentUser, getUserIp } from '@/api';
import { useNotification } from '@/composables/useNotification';
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
    const { openSupportChat, getUserData, getStartParam, hapticFeedback } = useTwaSdk();
    const { notify } = useNotification();

    const user = ref<{ first_name?: string }>({ first_name: 'user' });
    const usage = ref('');
    const subscriptionDate = ref('');
    const canClaimGift = ref(false);
    const userIp = ref('');
    
    onMounted(async () => {
      const userData = getUserData();
      if (userData?.first_name) {
        user.value.first_name = userData.first_name;
      }

      try {
        const startParam = getStartParam();
        if (startParam === 'subscription' && !sessionStorage.getItem('startParamHandled')) {
          sessionStorage.setItem('startParamHandled', 'true')
          router.push({ name: 'subscription' });
          return;
        }
        const currentUserData = await fetchCurrentUser(startParam);
        if (currentUserData) {
          usage.value = currentUserData.usage;
          subscriptionDate.value = currentUserData.subscriptionDate;
          canClaimGift.value = currentUserData.can_claim_gift;
        }

        const ipResponse = await getUserIp();
        if (ipResponse.ip) {
          userIp.value = ipResponse.ip;
        }
      } catch (error) {}
    });

    const goToVpn = () => {
      hapticFeedback('success');
      router.push({ name: 'vpn' });
    };

    const goToSubscription = () => {
      hapticFeedback('success');
      router.push({ name: 'subscription' });
    };

    const goToReferral = () => {
      hapticFeedback('success');
      router.push({ name: 'referral' });
    };

    const openSupport = () => {
      hapticFeedback('success');
      openSupportChat();
    };

    const claimGiftHandler = async () => {
      hapticFeedback('error');
      notify({ message: 'Уже воспользовались подарком', type: 'error' });
      if (!canClaimGift.value) { return; }
      try {
        const response = await claimGift();
        canClaimGift.value = false;
      } catch (error) {}
    };

    return {
      user,
      usage,
      subscriptionDate,
      userIp,
      goToVpn,
      goToSubscription,
      goToReferral,
      openSupport,
      claimGiftHandler,
    };
  },
});
</script>

<style scoped>
.dashboard-card {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 400px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
  overflow-y: auto;
  position: relative;
}

.dashboard-card::after {
  content: '';
  display: block;
  height: 50px;
  position: absolute;
  bottom: -50px;
  left: 0;
  right: 0;
  z-index: -1;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 20px;
}

.logo {
  width: 190px;
  height: 120px;
  align-self: center;
  margin-bottom: 10px;
}

.user-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
  flex-shrink: 0;
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

.ip-box {
  width: 100%;
  margin-bottom: 40px;
  max-height: 50px;
}

.ip-box .stats-box {
  padding: 12px;
}

.stats-container {
  display: flex;
  gap: 8px;
  width: 100%;
  margin-top: auto;
}

.stats-container .stats-box {
  flex: 1;
  height: auto;
}

.buttons-container {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 30px;
  flex-shrink: 0;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>