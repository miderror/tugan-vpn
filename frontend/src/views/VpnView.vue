<template>
  <div class="vpn-view">
    <BackButton />
    <div class="scrollable-content">
      <h1 class="setup-title">Быстрая настройка<br>VPN-сервиса</h1>
      <div class="content-container">
        <Stepper :steps="steps" :dividerHeights="dividerHeights" :activeStep="activeStep" />
        <div class="steps-container">
          <StepCard
              v-for="(step, index) in steps"
              :key="index"
              :stepNumber="index + 1"
              :description="stepDescriptions[index]"
              :isActive="activeStep === index + 1"
              :completed="step.completed"
              @toggle="handleStepToggle"
              @height-change="handleHeightChange(index, $event)"
          >
            <div v-if="activeStep === index + 1">
              <div v-if="index === 0">
                <button class="primary-button" @click.stop="openDownloadPage">
                  <SvgIcon :iconName="'download-icon'" class="download-icon" />
                  <span>Скачать</span>
                </button>
              </div>
              <div v-if="index === 1" class="step-buttons-container">
                <button class="primary-button" @click.stop="handleConnect">Подключиться</button>
                <span class="divider-text">или</span>
                <button class="secondary-button" @click.stop="handleCopyConfig">Скопировать конфиг</button>
              </div>
              <div v-if="index === 2">
                <p class="step-description">
                  При добавлении роутинга, сайты внутри страны будут открываться без VPN
                </p>
                <button class="primary-button" @click.stop="handleAddRule">
                  <SvgIcon :iconName="'russia-flag-icon'" class="flag-icon" />
                  <span class="rule-text">Добавить правило: Сайты РФ напрямую</span>
                </button>
              </div>
            </div>
          </StepCard>
        </div>
      </div>
      <InfoBanner class="info-banner" text="После того, как вы смогли добавить ваше подключение, вы можете вернуться сюда и ознакомиться с вашим личным кабинетом" />
    </div>
    <DashboardButton class="dashboard-button" />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useTwaSdk } from '@/composables/useTwaSdk';
import { fetchVpnConfig } from '@/api';
import { useNotification } from '@/composables/useNotification';
import Stepper from '@/components/Stepper.vue';
import StepCard from '@/components/StepCard.vue';
import SvgIcon from '@/components/SvgIcon.vue';
import InfoBanner from '@/components/InfoBanner.vue';
import DashboardButton from '@/components/DashboardButton.vue';
import BackButton from '@/components/BackButton.vue';

export default defineComponent({
  name: 'VpnView',
  components: {
    Stepper,
    StepCard,
    SvgIcon,
    InfoBanner,
    DashboardButton,
    BackButton,
  },
  setup() {
    const {
      openDownloadPageFromSdk, openSubscriptionLink, openRulesetLink,
      copyToClipboard, hapticFeedback
    } = useTwaSdk();
    const { notify } = useNotification();

    const steps = ref([
      { active: true, completed: false },
      { active: false, completed: false },
      { active: false, completed: false },
    ]);

    const stepDescriptions = [
      'Установить мобильное приложение',
      'Подключиться к VPN',
      'Добавить роутинг',
    ];

    const activeStep = ref(1);
    const dividerHeights = ref([58, 58, 58]);

    const handleStepToggle = (stepNumber: number) => {
      activeStep.value = stepNumber;
      steps.value = steps.value.map((step, index) => ({
        ...step,
        active: index + 1 === activeStep.value,
        completed: index + 1 < activeStep.value,
      }));
    };

    const handleHeightChange = (index: number, height: number) => {
      const circleHeight = 32;
      const gapHeight = 40;
      const dividerVerticalMargin = 16;
      dividerHeights.value[index] = height + gapHeight - circleHeight - dividerVerticalMargin;
    };

    const openDownloadPage = (): void => {
      hapticFeedback('success');
      openDownloadPageFromSdk();
    };

    // const handleConnect = async (): Promise<void> => {
    //   try {
    //     const response = await fetchVpnConfig();
    //     if (response.vpn_url) {
    //       const fullUrl = `${import.meta.env.VITE_API_URL}${response.vpn_url}`;
    //       openSubscriptionLink(fullUrl);
    //     }
    //   } catch (error) {}
    // };
    
    const handleConnect = (): void => {
      hapticFeedback('success');
      console.log("Fetching VPN config...");
      fetchVpnConfig()
        .then((response) => {
          console.log("VPN config fetched:", response);
          if (response.vpn_url) {
            const fullUrl = `${import.meta.env.VITE_API_URL}${response.vpn_url}`;
            console.log("Opening subscription link:", fullUrl);
            setTimeout(() => {
              openSubscriptionLink(fullUrl);
            }, 0);
            notify({ message: 'Конфигурация загружена', type: 'info' });
          } else {
            notify({ message: 'Ошибка: URL не найден', type: 'error' });
          }
        })
        .catch((error) => {
          console.error("Failed to fetch VPN config:", error);
          notify({ message: 'Ошибка загрузки конфигурации', type: 'error' });
        });
    };

    // const handleCopyConfig = async (): Promise<void> => {
    //   try {
    //     const response = await fetchVpnConfig();
    //     if (response.vpn_url) {
    //       const fullUrl = `${import.meta.env.VITE_API_URL}${response.vpn_url}`;
    //       copyToClipboard(fullUrl);
    //     }
    //     notify({ message: 'Скопировано', type: 'info' });
    //   } catch (error) {}
    // };

    const handleCopyConfig = (): void => {
      hapticFeedback('success');
      console.log("Fetching VPN config...");
      fetchVpnConfig()
        .then((response) => {
          console.log("VPN config fetched:", response);
          if (response.vpn_url) {
            const fullUrl = `${import.meta.env.VITE_API_URL}${response.vpn_url}`;
            console.log("Copying to clipboard:", fullUrl);
            setTimeout(() => {
              try {
                copyToClipboard(fullUrl);
                notify({ message: 'Скопировано', type: 'info' });
              } catch (error) {
                console.error("Failed to copy to clipboard:", error);
                notify({ message: 'Ошибка копирования', type: 'error' });
              }
            }, 0);
          }
        })
        .catch((error) => {
          console.error("Failed to fetch VPN config:", error);
          notify({ message: 'Ошибка загрузки конфигурации', type: 'error' });
        });
    };

    const handleAddRule = (): void => {
      hapticFeedback('success');
      console.log('Добавление правила...');
      const rulesetUrl = `${import.meta.env.VITE_API_URL}/ruleset/`;
      // const rulesetUrl = 'https://stridently-virtuous-squirrelfish.cloudpub.ru:443/ruleset.json';
      openRulesetLink(rulesetUrl);
    };


    return {
      steps,
      stepDescriptions,
      activeStep,
      dividerHeights,
      handleStepToggle,
      handleHeightChange,
      openDownloadPage,
      handleConnect,
      handleCopyConfig,
      handleAddRule,
    };
  },
});
</script>

<style scoped>
.vpn-view {
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

.setup-title {
  color: #737278;
  font-size: 18px;
  font-weight: 500;
  text-align: center;
  margin-bottom: 40px;
}

.content-container {
  flex: 1;
  display: flex;
  gap: 16px;
  margin-bottom: 40px;
}

.steps-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.step-buttons-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
}

.step-description {
  color: #898989;
  font-size: 14px;
  font-weight: 400;
  line-height: 17px;
}

.primary-button {
  width: 100%;
  border-radius: 12px;
  background-color: #121212;
  color: #ededed;
  padding: 16px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.secondary-button {
  width: 100%;
  border-radius: 12px;
  background-color: #fff;
  color: #121212;
  padding: 16px;
  font-weight: 600;
  border: 1px solid #dfdfdf;
  cursor: pointer;
  box-shadow: 0 4px 4px rgba(0, 0, 0, 0.1);
}

.divider-text {
  display: block;
  text-align: center;
  color: #737278;
  font-size: 14px;
  margin: 8px 0;
}

.flag-icon {
  width: 30px;
  height: 30px;
}

.download-icon {
  width: 17px;
  height: 17px;
}

.rule-text {
  text-align: left;
}

.info-banner {
  margin-top: auto;
}

.dashboard-button {
  flex-shrink: 0;
  margin-top: auto;
}
</style>