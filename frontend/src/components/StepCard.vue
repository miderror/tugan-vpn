<template>
  <div
    :class="['step-card', { active: isActive }]"
    @click="toggleStep"
    ref="stepCard"
  >
    <div class="step-header">
      <div class="step-text">
        <h2 v-if="!completed" :class="['step-title', { 'active-text': isActive }]">Шаг {{ stepNumber }}</h2>
        <p :class="['step-description', { 'active-text': isActive }]">{{ description }}</p>
      </div>
      <SvgIcon
        :iconName="isActive ? 'chevron-up-icon' : 'chevron-down-icon'"
        class="step-icon"
      />
    </div>
    <div v-if="isActive" class="step-content">
      <slot></slot>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUpdated } from 'vue';
import SvgIcon from './SvgIcon.vue';

export default defineComponent({
  name: 'StepCard',
  components: {
    SvgIcon,
  },
  props: {
    stepNumber: {
      type: Number,
      required: true,
    },
    description: {
      type: String,
      required: true,
    },
    isActive: {
      type: Boolean,
      default: false,
    },
    completed: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['toggle', 'height-change'],
  setup(props, { emit }) {
    const stepCard = ref<HTMLElement | null>(null);

    const toggleStep = () => {
      emit('toggle', props.stepNumber);
    };

    const updateHeight = () => {
      if (stepCard.value) {
        const height = stepCard.value.offsetHeight;
        emit('height-change', height);
      }
    };

    onMounted(updateHeight);
    onUpdated(updateHeight);

    return {
      stepCard,
      toggleStep,
    };
  },
});
</script>

<style scoped>
.step-card {
  border-radius: 16px;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  padding: 16px;
  cursor: pointer;
}

/* .step-card.active {
  border: 1px solid #121212;
} */

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: stretch;
}

.step-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.step-title {
  color: #737278;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.step-description {
  color: #737278;
  font-size: 14px;
  font-weight: 600;
  margin: 0;
}

.active-text {
  color: #121212;
}

.step-icon {
  width: 20px;
  height: 20px;
}
</style>