<template>
  <div class="referral-view">
    <div class="scrollable-content">
      <h1 class="referral-title">Реферальная<br>программа</h1>
      <div class="stats-container">
        <StatsBox label="Ваш реферальный баланс:" :value="referralBalance" />
        <StatsBox label="Ваши рефералы:" :value="referralCount" />
      </div>
      <ReferralLink :referralLink="referralLink" />
      <div class="referral-list">
        <ReferralUser v-for="user in referralUsers" :key="user.id" :user="user" />
      </div>
      <InfoBanner text="С каждого вашего реферала вы будете получать дополнительные 2 недели доступа" />
    </div>
    <DashboardButton />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getTelegramUserAvatar } from '@/api';
import { useTwaSdk } from '@/composables/useTwaSdk';
import StatsBox from '@/components/StatsBox.vue';
import ReferralLink from '@/components/ReferralLink.vue';
import ReferralUser from '@/components/ReferralUser.vue';
import InfoBanner from '@/components/InfoBanner.vue';
import DashboardButton from '@/components/DashboardButton.vue';

export default defineComponent({
  name: 'ReferralView',
  components: {
    StatsBox,
    ReferralLink,
    ReferralUser,
    InfoBanner,
    DashboardButton,
  },
  setup() {
    const router = useRouter();
    const { getUserData } = useTwaSdk();
    const referralBalance = ref(100);
    const referralCount = ref(2);
    const referralLink = ref('https://t.me/your_referral_link');
    const referralUsers = ref([
      {
        id: 1699267593,
        username: 'user1',
        avatar: '',
      },
      {
        id: 1699267593,
        username: 'user2',
        avatar: '',
      },
      {
        id: 1699267593,
        username: 'user2',
        avatar: '',
      },
      {
        id: 2,
        username: 'user2',
        avatar: '',
      },
      {
        id: 2,
        username: 'user2',
        avatar: '',
      },
      {
        id: 1699267593,
        username: 'user2',
        avatar: '',
      },
    ]);

    onMounted(async () => {
      const userData = getUserData();
      if (userData?.id) {
        const botUsername = import.meta.env.VITE_BOT_USERNAME;
        const appName = import.meta.env.VITE_APP_NAME;
        referralLink.value = `https://t.me/${botUsername}/${appName}?startapp=${userData.id}`;
      }

      for (const user of referralUsers.value) {
        user.avatar = (await getTelegramUserAvatar(user.id)) || '';
      }
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
}

.info-banner {
  margin-top: auto;
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
  margin: 10px 0px;
}

.dashboard-button {
  flex-shrink: 0;
}
</style>