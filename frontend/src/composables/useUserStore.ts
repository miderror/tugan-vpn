import { ref, computed } from "vue";
import { fetchCurrentUser } from "@/api";
import { useTwaSdk } from "@/composables/useTwaSdk";

const { getUserData } = useTwaSdk();
const twaUser = getUserData();

const userState = ref({
  first_name: twaUser?.first_name || "Пользователь",
  usage: "",
  subscription_date: "",
  can_claim_gift: false,
  ip: "",
  vpn_url: "",
});

const isLoading = ref(false);

export function useUserStore() {
  const loadUser = async () => {
    if (isLoading.value) return;

    isLoading.value = true;

    try {
      const data = await fetchCurrentUser();

      userState.value = {
        ...userState.value,
        usage: data.usage,
        subscription_date: data.subscription_date,
        can_claim_gift: data.can_claim_gift,
        ip: data.ip,
        vpn_url: data.vpn_url,
      };
    } catch (e) {
      console.error("Data update error:", e);
    } finally {
      isLoading.value = false;
    }
  };

  return {
    user: computed(() => userState.value),
    isLoading: computed(() => isLoading.value),
    loadUser,
  };
}
