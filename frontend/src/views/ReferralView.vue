<template>
  <div class="referral-view">
    <BackButton />
    <div class="scrollable-content">
      <h1 class="referral-title">Реферальная<br>программа</h1>
      <div class="stats-container">
        <StatsBox label="Ваш реферальный баланс:" :value="`${referralBalance}₽`" />
        <StatsBox label="Ваши рефералы:" :value="referralCount" />
      </div>
      <ReferralLink :referralLink="referralLink" />
      <div class="referral-list">
        <ReferralUser v-for="user in referralUsers" :key="user.id" :user="user" />
      </div>
      <InfoBanner class="info-banner" text="С каждого приведённого друга вы будете получать 100₽ на баланс" />
    </div>
    <DashboardButton class="dashboard-button" />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { fetchReferralData, getTelegramUserAvatar } from '@/api';
import { useTwaSdk } from '@/composables/useTwaSdk';
import StatsBox from '@/components/StatsBox.vue';
import ReferralLink from '@/components/ReferralLink.vue';
import ReferralUser from '@/components/ReferralUser.vue';
import InfoBanner from '@/components/InfoBanner.vue';
import DashboardButton from '@/components/DashboardButton.vue';
import BackButton from '@/components/BackButton.vue';

export default defineComponent({
  name: 'ReferralView',
  components: {
    StatsBox,
    ReferralLink,
    ReferralUser,
    InfoBanner,
    DashboardButton,
    BackButton,
  },
  setup() {
    const { getUserData } = useTwaSdk();
    const referralBalance = ref(0);
    const referralCount = ref(0);
    const referralLink = ref('https://t.me/your_referral_link');
    const referralUsers = ref<{ id: number; username: string; avatar: () => Promise<string | null> }[]>([]);

    onMounted(async () => {
      const userData = getUserData();
      if (userData?.id) {
        const botUsername = import.meta.env.VITE_BOT_USERNAME;
        const appName = import.meta.env.VITE_APP_NAME;
        referralLink.value = `https://t.me/${botUsername}/${appName}?startapp=${userData.id}`;
      }

      try {
        const referralData = await fetchReferralData() as { id: number; username: string }[];
        referralUsers.value = referralData.map(user => ({
          id: user.id,
          username: user.username,
          avatar: getTelegramUserAvatar(user.id),
        }));
        referralCount.value = referralData.length;
        referralBalance.value = referralData.length * 100;
      } catch (error) {}
    });

    return {
      referralBalance,
      referralCount,
      referralLink,
      referralUsers,
    };
  },
});
</script>

<style scoped>
.referral-view {
  max-width: 480px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 100vh;
  box-sizing: border-box;
}

.scrollable-content {
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding-bottom: 20px;
  flex: 1;
}

.info-banner {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-style: normal;
  margin-top: auto;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.referral-title {
  color: #121212;
  font-size: 26px;
  font-weight: 600;
  line-height: 31px;
  text-align: center;
  margin-bottom: 40px;
}

.stats-container {
  display: flex;
  gap: 8px;
  margin-bottom: 40px;
}

.stats-container .stats-box {
  font-size: 14px;
  height: auto;
}

.referral-list {
  margin: 12px 0px;
}

.dashboard-button {
  flex-shrink: 0;
  margin-top: auto
}
</style>