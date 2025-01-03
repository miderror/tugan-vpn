import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '@/views/HomeView.vue';
import VpnView from '@/views/VpnView.vue';
import ReferralView from '@/views/ReferralView.vue';
import SubscriptionView from '@/views/SubscriptionView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/vpn',
      name: 'vpn',
      component: VpnView,
    },
    {
      path: '/referral',
      name: 'referral',
      component: ReferralView,
    },
    {
      path: '/subscription',
      name: 'subscription',
      component: SubscriptionView,
    },
  ],
});

export default router;