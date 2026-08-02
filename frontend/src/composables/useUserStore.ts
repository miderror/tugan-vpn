import { ref, computed } from "vue";
import { fetchCurrentUser } from "@/api";
import { useTwaSdk } from "@/composables/useTwaSdk";
import type { UserMeApiResponse } from "@/types";

const { getUserData } = useTwaSdk();
const twaUser = getUserData();

const userState = ref({
  first_name: twaUser?.first_name || "Пользователь",
  usage: "",
  subscription_date: "",
  ip: "",
  vpn_url: "",
  can_claim_gift: false,
  tried_to_connect: false,
  is_active: false,
});


const isLoading = ref(false);

function formatBytes(bytes: number): string {
  if (!bytes || bytes < 0) {
    return "0.0/250.0 GB";
  }
  const gb = bytes / (1024 * 1024 * 1024);
  return `${gb.toFixed(1)}/250 GB`;
}

function formatDate(isoString: string): string {
  if (!isoString) return "—";
  const date = new Date(isoString);
  return date.toLocaleDateString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

export function useUserStore() {
  const loadUser = async () => {
    if (isLoading.value) return;
    isLoading.value = true;

    try {
      const data: UserMeApiResponse = await fetchCurrentUser();
      const flags = data.f || 0;

      const claimedGift = (flags & 1) !== 0;
      const triedToConnect = (flags & 2) !== 0;
      const isActiveVpn = (flags & 4) !== 0;

      userState.value = {
        ...userState.value,
        usage: formatBytes(data.ub || 0),
        subscription_date: formatDate(data.exp),
        ip: data.ip || "127.0.0.1",
        vpn_url: data.at ? `/api/sub/${data.at}` : "",
        can_claim_gift: !claimedGift,
        tried_to_connect: triedToConnect,
        is_active: isActiveVpn,
      };
    } catch (e) {
      console.error("User store sync error:", e);
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
