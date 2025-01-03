<template>
  <div class="vpn-view">
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
      <InfoBanner text="После того, как вы смогли добавить ваше подключение, вы можете вернуться
      сюда и ознакомиться с вашим личным кабинетом"/>
    </div>
    <DashboardButton />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import Stepper from '../components/Stepper.vue';
import StepCard from '../components/StepCard.vue';
import SvgIcon from '../components/SvgIcon.vue';
import InfoBanner from '../components/InfoBanner.vue';
import DashboardButton from '../components/DashboardButton.vue';

export default defineComponent({
  name: 'VpnView',
  components: {
    Stepper,
    StepCard,
    SvgIcon,
    InfoBanner,
    DashboardButton,
  },
  setup() {
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
      console.log('Скачивание приложения...');
    };

    const handleConnect = (): void => {
      console.log('Подключение к VPN...');
    };

    const handleCopyConfig = (): void => {
      console.log('Копирование конфигурации...');
    };

    const handleAddRule = (): void => {
      console.log('Добавление правила...');
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
  overflow-y: auto;
  padding-bottom: 20px;
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
</style>